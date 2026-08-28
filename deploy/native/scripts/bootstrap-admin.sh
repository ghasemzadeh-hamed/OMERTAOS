#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/current}"
INSTALLER_ENV=/etc/omertaos/installer.env
CONSOLE_ENV=/etc/omertaos/console.env
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_install-lib.sh
source "$SCRIPT_DIR/_install-lib.sh"

usage() { cat <<'EOF'
Usage: bootstrap-admin.sh [--root PATH] [--installer-env PATH]
       [--console-env PATH] [--dry-run|--check] [--help]

Create the first Console administrator only when the user table is empty.
Repeated runs preserve the existing admin password. --check is read-only.
EOF
}
while (($#)); do case "$1" in
  --root) (($# >= 2)) || native_die '--root requires a path'; ROOT="$2"; shift ;;
  --installer-env) (($# >= 2)) || native_die '--installer-env requires a path'; INSTALLER_ENV="$2"; shift ;;
  --console-env) (($# >= 2)) || native_die '--console-env requires a path'; CONSOLE_ENV="$2"; shift ;;
  --dry-run) DRY_RUN=true ;; --check) CHECK_ONLY=true ;;
  --help|-h) usage; exit 0 ;; *) native_die "unknown argument: $1" ;;
esac; shift; done
"$DRY_RUN" && "$CHECK_ONLY" && native_die '--dry-run and --check are mutually exclusive'
native_require_linux
((EUID == 0)) || native_die 'run as root so bootstrap credentials remain root-readable only'
native_prepare_runner
native_require_node

declare -A INSTALL_CONFIG=() CONSOLE_CONFIG=()
native_load_env_file "$INSTALLER_ENV" INSTALL_CONFIG
native_load_env_file "$CONSOLE_ENV" CONSOLE_CONFIG
email="${INSTALL_CONFIG[OMERTAOS_CONSOLE_ADMIN_EMAIL]:-}"
password="${INSTALL_CONFIG[OMERTAOS_CONSOLE_ADMIN_PASSWORD]:-}"
name="${INSTALL_CONFIG[OMERTAOS_CONSOLE_ADMIN_NAME]:-OMERTAOS Administrator}"
min_length="${INSTALL_CONFIG[OMERTAOS_CONSOLE_ADMIN_PASSWORD_MIN_LENGTH]:-8}"
max_length="${INSTALL_CONFIG[OMERTAOS_CONSOLE_ADMIN_PASSWORD_MAX_LENGTH]:-32}"
database_url="${CONSOLE_CONFIG[DATABASE_URL]:-}"
[[ "$email" == *@* && "$email" != CHANGE_ME ]] || native_die 'an explicit Console admin email is required'
[[ "$min_length" =~ ^[0-9]+$ && "$max_length" =~ ^[0-9]+$ ]] || native_die 'Console admin password length bounds must be integers'
((min_length >= 8)) || native_die 'Console admin password minimum cannot be less than 8'
((max_length >= min_length && max_length <= 72)) || native_die 'Console admin password maximum must be between the configured minimum and 72'
[[ ${#password} -ge min_length && ${#password} -le max_length && "$password" != CHANGE_ME && "$password" != admin123 ]] || native_die "Console admin password must be non-default and between $min_length and $max_length characters"
[[ "$database_url" == postgresql://* || "$database_url" == postgres://* ]] || native_die 'Console DATABASE_URL must use PostgreSQL'
[[ "$database_url" != *CHANGE_ME* ]] || native_die 'N5 refuses placeholder database credentials'
entrypoint="$ROOT/console/scripts/dist/bootstrap-admin.js"
[[ -f "$entrypoint" ]] || native_die 'compiled Console bootstrap entrypoint is missing; rerun the N4 Console installer'

if "$DRY_RUN"; then
  printf 'DRY-RUN: bootstrap Console admin as omertaos with database/password values redacted\n'
else
  check_value=0
  "$CHECK_ONLY" && check_value=1
  native_run_service env DATABASE_URL="$database_url" CONSOLE_ADMIN_EMAIL="$email" \
    CONSOLE_ADMIN_PASSWORD="$password" CONSOLE_ADMIN_NAME="$name" \
    CONSOLE_ADMIN_PASSWORD_MIN_LENGTH="$min_length" CONSOLE_ADMIN_PASSWORD_MAX_LENGTH="$max_length" \
    CONSOLE_BOOTSTRAP_CHECK="$check_value" SKIP_CONSOLE_SEED=0 \
    node "$entrypoint"
  if ! "$CHECK_ONLY"; then
    native_run_service env DATABASE_URL="$database_url" CONSOLE_ADMIN_EMAIL="$email" \
      CONSOLE_ADMIN_PASSWORD="$password" CONSOLE_ADMIN_NAME="$name" \
      CONSOLE_ADMIN_PASSWORD_MIN_LENGTH="$min_length" CONSOLE_ADMIN_PASSWORD_MAX_LENGTH="$max_length" \
      CONSOLE_BOOTSTRAP_CHECK=1 SKIP_CONSOLE_SEED=0 \
      node "$entrypoint"
  fi
fi
printf 'N5 Console administrator bootstrap completed without credential rotation.\n'
