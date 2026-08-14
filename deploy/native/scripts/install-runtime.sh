#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
CHECK_ONLY=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/current}"
DEST="${OMERTAOS_RUNTIME_BIN_DIR:-/var/lib/omertaos/bin}"
TARGET="${OMERTAOS_RUNTIME_TARGET_DIR:-/var/lib/omertaos/build/runtime}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=_install-lib.sh
source "$SCRIPT_DIR/_install-lib.sh"

usage() { cat <<'EOF'
Usage: install-runtime.sh [--root PATH] [--dest PATH] [--target PATH]
       [--dry-run|--check] [--help]

Build Runtime with Cargo.lock into writable state and install only the release
binary. The daemon is never started and no unsupported CLI flags are used.
EOF
}
while (($#)); do case "$1" in
  --root) (($# >= 2)) || native_die '--root requires a path'; ROOT="$2"; shift ;;
  --dest) (($# >= 2)) || native_die '--dest requires a path'; DEST="$2"; shift ;;
  --target) (($# >= 2)) || native_die '--target requires a path'; TARGET="$2"; shift ;;
  --dry-run) DRY_RUN=true ;; --check) CHECK_ONLY=true ;;
  --help|-h) usage; exit 0 ;; *) native_die "unknown argument: $1" ;;
esac; shift; done
"$DRY_RUN" && "$CHECK_ONLY" && native_die '--dry-run and --check are mutually exclusive'
native_require_linux
native_prepare_runner
command -v cargo >/dev/null || native_die 'cargo is required; complete N2 first'
command -v rustc >/dev/null || native_die 'rustc is required; complete N2 first'
MANIFEST="$ROOT/runtime-daemon/Cargo.toml"
LOCK="$ROOT/runtime-daemon/Cargo.lock"
[[ -f "$MANIFEST" ]] || native_die 'runtime-daemon/Cargo.toml is missing'
[[ -f "$LOCK" ]] || native_die 'runtime-daemon/Cargo.lock is required for reproducible N4 installation'

if ! "$CHECK_ONLY"; then
  native_prepare_dir /var/lib/omertaos/cache/cargo
  native_prepare_dir "$TARGET"
  native_prepare_dir "$DEST"
  native_run_service env CARGO_HOME=/var/lib/omertaos/cache/cargo CARGO_TARGET_DIR="$TARGET" \
    cargo build --locked --release --manifest-path "$MANIFEST"
  SOURCE="$TARGET/release/runtime-daemon"
  if ! "$DRY_RUN"; then [[ -x "$SOURCE" ]] || native_die 'Runtime release binary was not created'; fi
  if "$DRY_RUN"; then native_print_command install -m 0755 "$SOURCE" "$DEST/runtime-daemon"
  else install -m 0755 "$SOURCE" "$DEST/runtime-daemon"; fi
fi
if ! "$DRY_RUN"; then [[ -x "$DEST/runtime-daemon" ]] || native_die 'installed Runtime binary is missing'; fi
printf 'N4 Runtime build/install checks completed; the daemon was not started.\n'
