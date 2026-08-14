#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
START=false
PROFILE=lite
VERSION=
SOURCE=
BACKUP=
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"
usage() {
  cat <<'EOF'
Usage: first-boot.sh --version VERSION --backup PATH
       [--source PATH] [--profile lite|full|enterprise]
       [--dry-run] [--start] [--help]

Install host/data prerequisites, then delegate the initial immutable release,
migrations, active-link creation, and systemd installation to N8 update.sh.
Services remain stopped unless --start is explicitly supplied.
EOF
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
while (($#)); do
  case "$1" in
    --version) (($# >= 2)) || die '--version requires a value'; VERSION="$2"; shift ;;
    --backup) (($# >= 2)) || die '--backup requires a path'; BACKUP="$2"; shift ;;
    --source) (($# >= 2)) || die '--source requires a path'; SOURCE="$2"; shift ;;
    --profile) (($# >= 2)) || die '--profile requires a value'; PROFILE="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --start) START=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done
[[ "$(uname -s)" == Linux ]] || die 'first boot requires Linux'
case "$PROFILE" in lite|full|enterprise) ;; *) die "unsupported profile: $PROFILE" ;; esac
[[ -n "$VERSION" && -n "$BACKUP" ]] || die '--version and --backup are required'
[[ -n "$SOURCE" ]] || SOURCE="$REPO_ROOT"

installer_args=(--profile "$PROFILE")
"$DRY_RUN" && installer_args+=(--dry-run)
for installer in install-os-packages.sh install-data-services.sh; do
  [[ -x "$SCRIPT_DIR/$installer" ]] || die "missing executable installer: $installer"
  "$SCRIPT_DIR/$installer" "${installer_args[@]}"
done

update_args=(--version "$VERSION" --source "$SOURCE" --backup "$BACKUP")
"$DRY_RUN" && update_args+=(--dry-run)
"$START" && update_args+=(--start)
"$SCRIPT_DIR/update.sh" "${update_args[@]}"
printf 'Native first boot completed through immutable release activation.\n'
