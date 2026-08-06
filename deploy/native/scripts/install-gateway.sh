#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/current}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_install-lib.sh
source "$SCRIPT_DIR/_install-lib.sh"

usage() { cat <<'EOF'
Usage: install-gateway.sh [--root PATH] [--dry-run|--check] [--help]

Install the locked Gateway dependency graph and build dist/server.js as the
non-root omertaos account. No service is started.
EOF
}
while (($#)); do case "$1" in
  --root) (($# >= 2)) || native_die '--root requires a path'; ROOT="$2"; shift ;;
  --dry-run) DRY_RUN=true ;; --check) CHECK_ONLY=true ;;
  --help|-h) usage; exit 0 ;; *) native_die "unknown argument: $1" ;;
esac; shift; done
"$DRY_RUN" && "$CHECK_ONLY" && native_die '--dry-run and --check are mutually exclusive'
native_require_linux
native_prepare_runner
native_require_node
SERVICE="$ROOT/gateway"
[[ -f "$SERVICE/package.json" ]] || native_die 'gateway/package.json is missing'
[[ -f "$SERVICE/package-lock.json" ]] || native_die 'gateway/package-lock.json is required for reproducible N4 installation'

if ! "$CHECK_ONLY"; then
  native_assert_service_writable "$SERVICE"
  native_prepare_dir /var/lib/omertaos/cache/npm
  native_run_service env npm_config_cache=/var/lib/omertaos/cache/npm npm ci --prefix "$SERVICE" --no-audit --no-fund
  native_run_service npm run build --prefix "$SERVICE"
fi
if ! "$DRY_RUN"; then
  [[ -f "$SERVICE/dist/server.js" ]] || native_die 'Gateway build did not create dist/server.js'
  native_run_service npm ls --prefix "$SERVICE" --omit=dev --depth=0 >/dev/null
fi
printf 'N4 Gateway build/install checks completed; no service was started.\n'
