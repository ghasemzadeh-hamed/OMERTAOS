#!/usr/bin/env bash
set -euo pipefail

VERSION=
SOURCE=
BACKUP=
START=false
DRY_RUN=false
RELEASES=/opt/omertaos/releases
CURRENT=/opt/omertaos/current
PREVIOUS=/opt/omertaos/previous
LOCK=/var/lib/omertaos/update.lock

usage() {
  cat <<'EOF'
Usage: update.sh --version VERSION --source PATH --backup PATH [--start] [--dry-run] [--help]

Build an immutable Native release, apply forward-only migrations, and atomically
activate it. BACKUP must be an existing, non-empty external backup outside
/opt/omertaos and /var/lib/omertaos. No database downgrade or release deletion
is performed. Services start only with --start or when the target was active.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
print_command() { printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'; }
run() { if "$DRY_RUN"; then print_command "$@"; else "$@"; fi; }

while (($#)); do
  case "$1" in
    --version) (($# >= 2)) || die '--version requires a value'; VERSION="$2"; shift ;;
    --source) (($# >= 2)) || die '--source requires a path'; SOURCE="$2"; shift ;;
    --backup) (($# >= 2)) || die '--backup requires a path'; BACKUP="$2"; shift ;;
    --start) START=true ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'Native update requires Linux'
((EUID == 0)) || die 'run as root'
[[ "$VERSION" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'invalid release version'
[[ -n "$SOURCE" && -n "$BACKUP" ]] || die '--source and --backup are required'
for executable in flock readlink rsync sha256sum systemctl install mv ln find date chown pg_restore tar git sort xargs awk hostname python3 node npm cargo rustc; do
  command -v "$executable" >/dev/null || die "missing required executable: $executable"
done

[[ -e "$SOURCE" ]] || die 'source path does not exist'
[[ -e "$BACKUP" ]] || die 'verified external backup does not exist'
SOURCE="$(readlink -f -- "$SOURCE")"
BACKUP="$(readlink -f -- "$BACKUP")"
[[ -d "$SOURCE" && -f "$SOURCE/pyproject.toml" && -d "$SOURCE/deploy/native" ]] \
  || die 'source is not an OMERTAOS checkout'
git -C "$SOURCE" rev-parse --is-inside-work-tree >/dev/null 2>&1 || die 'source must be a Git worktree'
source_commit="$(git -C "$SOURCE" rev-parse HEAD)"
source_branch="$(git -C "$SOURCE" branch --show-current)"
[[ -n "$source_branch" ]] || source_branch=detached
[[ -z "$(git -C "$SOURCE" status --porcelain --untracked-files=normal)" ]] \
  || die 'source worktree must be clean for a reproducible release'
[[ -d "$BACKUP" ]] || die 'backup must be a canonical backup directory'
case "$BACKUP" in
  /opt/omertaos|/opt/omertaos/*|/var/lib/omertaos|/var/lib/omertaos/*)
    die 'backup must be external to installation and persistent-state roots' ;;
esac
case "$SOURCE" in
  "$RELEASES"|"$RELEASES"/*) die 'source must be outside the immutable releases directory' ;;
esac
"$SOURCE/deploy/native/scripts/restore.sh" --backup "$BACKUP"

release="$RELEASES/$VERSION"
staging="$RELEASES/.staging-$VERSION-$$"

if "$DRY_RUN"; then
  printf 'DRY-RUN: verified external backup %q before any migration\n' "$BACKUP"
  printf 'DRY-RUN: acquire exclusive lock %q\n' "$LOCK"
else
  install -d -o root -g root -m 0755 "$RELEASES"
  install -d -o root -g root -m 0750 "$(dirname "$LOCK")"
  exec 9>"$LOCK"
  flock -n 9 || die 'another update or rollback is in progress'
fi
[[ ! -e "$release" && ! -e "$staging" ]] || die 'release version or staging path already exists'

old_current=
if [[ -L "$CURRENT" ]]; then
  old_current="$(readlink -f -- "$CURRENT")"
  case "$old_current" in "$RELEASES"/*) ;; *) die 'current points outside immutable releases' ;; esac
  [[ -f "$old_current/release.manifest.sha256" ]] || die 'current release checksum manifest is missing'
  (cd "$old_current" && sha256sum --check release.manifest.sha256)
elif [[ -e "$CURRENT" ]]; then
  die 'current must be a symlink or absent'
fi

run install -d -o omertaos -g omertaos -m 0755 "$staging"
run rsync -a \
  --exclude=.git --exclude=.env --exclude=node_modules --exclude=.next \
  --exclude=dist --exclude=target --exclude=__pycache__ \
  "$SOURCE/" "$staging/"

run "$staging/deploy/native/scripts/install-control.sh" \
  --root "$staging" --venv "$staging/.venv/control"
run "$staging/deploy/native/scripts/install-gateway.sh" --root "$staging"
run "$staging/deploy/native/scripts/install-console.sh" --root "$staging"
run "$staging/deploy/native/scripts/install-runtime.sh" \
  --root "$staging" --dest "$staging/bin" \
  --target "/var/lib/omertaos/build/runtime-$VERSION"

if ! "$DRY_RUN"; then
  [[ -x "$staging/.venv/control/bin/python" ]] || die 'Control artifact is missing'
  [[ -f "$staging/gateway/dist/server.js" ]] || die 'Gateway artifact is missing'
  [[ -f "$staging/console/.next/BUILD_ID" ]] || die 'Console artifact is missing'
  [[ -x "$staging/bin/runtime-daemon" ]] || die 'Runtime artifact is missing'
  backup_manifest_sha256="$(sha256sum "$BACKUP/backup.manifest.sha256" | awk '{print $1}')"
  {
    printf 'format_version=1\n'
    printf 'version=%s\ncreated_utc=%s\n' "$VERSION" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    printf 'source_commit=%s\nsource_branch=%s\n' "$source_commit" "$source_branch"
    printf 'backup_manifest_sha256=%s\n' "$backup_manifest_sha256"
    printf 'host=%s\n' "$(hostname)"
    printf 'python=%s\n' "$(python3 --version 2>&1)"
    printf 'node=%s\nnpm=%s\n' "$(node --version)" "$(npm --version)"
    printf 'rustc=%s\ncargo=%s\n' "$(rustc --version)" "$(cargo --version)"
  } > "$staging/release.metadata"
  (
    cd "$staging"
    find . -type f ! -path './release.manifest.sha256' -print0 \
      | sort -z | xargs -0 sha256sum > release.manifest.sha256
    sha256sum --check release.manifest.sha256
  )
  chown -R root:root "$staging"
  mv -T "$staging" "$release"
else
  printf 'DRY-RUN: record clean Git commit/branch, backup manifest hash, host, and toolchain versions\n'
  print_command sha256sum '<all release files>' '>' "$staging/release.manifest.sha256"
  print_command mv -T "$staging" "$release"
fi

run "$release/deploy/native/scripts/migrate-database.sh" \
  --root "$release" --venv "$release/.venv/control"
run "$release/deploy/native/scripts/bootstrap-admin.sh" --root "$release"

was_active=false
if systemctl is-active --quiet omertaos.target; then was_active=true; fi

activate_link() {
  local target="$1" link="$2" temporary="${link}.new.$$"
  run ln -s "$target" "$temporary"
  run mv -Tf "$temporary" "$link"
}

restore_previous() {
  trap - ERR
  [[ -n "$old_current" ]] || return 0
  printf 'ERROR: post-activation validation failed; restoring prior code release. Database changes remain forward-only.\n' >&2
  activate_link "$old_current" "$CURRENT"
  "$old_current/deploy/native/scripts/install-systemd.sh" || true
  if "$was_active" || "$START"; then systemctl start omertaos.target || true; fi
}

if "$was_active"; then run systemctl stop omertaos.target; fi
if [[ -n "$old_current" ]]; then activate_link "$old_current" "$PREVIOUS"; fi
activate_link "$release" "$CURRENT"

if "$DRY_RUN"; then
  print_command "$release/deploy/native/scripts/install-systemd.sh"
  if "$was_active" || "$START"; then
    print_command systemctl start omertaos.target
    print_command "$release/deploy/native/scripts/smoke-test.sh" --mode native
  fi
else
  trap restore_previous ERR
  "$release/deploy/native/scripts/install-systemd.sh"
  if "$was_active" || "$START"; then
    systemctl start omertaos.target
    "$release/deploy/native/scripts/smoke-test.sh" --mode native
  fi
  trap - ERR
fi

printf 'N8 release %s activated. Persistent state/configuration were preserved; database rollback was not attempted.\n' "$VERSION"
