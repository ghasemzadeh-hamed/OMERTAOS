#!/usr/bin/env bash
set -euo pipefail

VERSION=
START=false
DRY_RUN=false
CHECK_ONLY=false
RELEASES=/opt/omertaos/releases
CURRENT=/opt/omertaos/current
PREVIOUS=/opt/omertaos/previous
LOCK=/var/lib/omertaos/update.lock

usage() {
  cat <<'EOF'
Usage: rollback.sh [--version VERSION] [--start] [--dry-run|--check] [--help]

Atomically switch current to a verified immutable release. Without --version,
the previous symlink is selected. Code rollback never downgrades databases,
deletes a release, disables units, or removes configuration/persistent state.
EOF
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
print_command() { printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'; }

while (($#)); do
  case "$1" in
    --version) (($# >= 2)) || die '--version requires a value'; VERSION="$2"; shift ;;
    --start) START=true ;;
    --dry-run) DRY_RUN=true ;;
    --check) CHECK_ONLY=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done
"$DRY_RUN" && "$CHECK_ONLY" && die '--dry-run and --check are mutually exclusive'

[[ "$(uname -s)" == Linux ]] || die 'native rollback requires Linux'
((EUID == 0)) || die 'run as root'
for executable in flock readlink sha256sum systemctl mv ln; do
  command -v "$executable" >/dev/null || die "missing required executable: $executable"
done
if "$DRY_RUN"; then
  printf 'DRY-RUN: acquire exclusive lock %q\n' "$LOCK"
elif ! "$CHECK_ONLY"; then
  exec 9>"$LOCK"
  flock -n 9 || die 'another update or rollback is in progress'
fi

if [[ -n "$VERSION" ]]; then
  [[ "$VERSION" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || die 'invalid release version'
  target="$RELEASES/$VERSION"
else
  [[ -L "$PREVIOUS" ]] || die 'previous release symlink is missing; pass --version'
  target="$(readlink -f -- "$PREVIOUS")"
fi
[[ -e "$target" ]] || die 'rollback target does not exist'
target="$(readlink -f -- "$target")"
case "$target" in "$RELEASES"/*) ;; *) die 'rollback target is outside immutable releases' ;; esac
[[ -d "$target" && -f "$target/release.manifest.sha256" ]] || die 'rollback release or checksum manifest is missing'
(cd "$target" && sha256sum --check release.manifest.sha256)
[[ -L "$CURRENT" ]] || die 'current release symlink is missing'
old_current="$(readlink -f -- "$CURRENT")"
[[ "$target" != "$old_current" ]] || die 'rollback target is already current'

run() {
  if "$DRY_RUN"; then print_command "$@"; else "$@"; fi
}

if "$CHECK_ONLY"; then
  printf 'N8 rollback check passed for %s; no link, service, database, or state change occurred.\n' "$target"
  exit 0
fi
was_active=false
if systemctl is-active --quiet omertaos.target; then was_active=true; fi
activate_link() {
  local value="$1" link="$2" temporary="${link}.new.$$"
  run ln -s "$value" "$temporary"
  run mv -Tf "$temporary" "$link"
}
restore_current() {
  trap - ERR
  printf 'ERROR: rollback validation failed; restoring the original code release. Database state was untouched.\n' >&2
  activate_link "$old_current" "$CURRENT"
  activate_link "$target" "$PREVIOUS"
  "$old_current/deploy/native/scripts/install-systemd.sh" || true
  if "$was_active" || "$START"; then systemctl start omertaos.target || true; fi
}

if "$was_active"; then run systemctl stop omertaos.target; fi
activate_link "$old_current" "$PREVIOUS"
activate_link "$target" "$CURRENT"
if "$DRY_RUN"; then
  print_command "$target/deploy/native/scripts/install-systemd.sh"
  if "$was_active" || "$START"; then
    print_command systemctl start omertaos.target
    print_command "$target/deploy/native/scripts/smoke-test.sh" --mode native
  fi
else
  trap restore_current ERR
  "$target/deploy/native/scripts/install-systemd.sh"
  if "$was_active" || "$START"; then
    systemctl start omertaos.target
    "$target/deploy/native/scripts/smoke-test.sh" --mode native
  fi
  trap - ERR
fi
printf 'N8 code rollback activated %s. Configuration/data were preserved and no database downgrade was attempted.\n' "$target"
