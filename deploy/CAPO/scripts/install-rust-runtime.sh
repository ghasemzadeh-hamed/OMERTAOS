#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/OMERTAOS}"
DEST="${OMERTAOS_RUNTIME_BIN_DIR:-/var/lib/omertaos/bin}"

usage() {
  cat <<'EOF'
Usage: install-rust-runtime.sh [--root PATH] [--dest PATH] [--dry-run] [--help]

Build the canonical runtime-daemon release binary and install it into the CAPO
application state directory. The installer does not start the daemon or pass
unsupported runtime CLI flags.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'; else "$@"; fi
}

while (($#)); do
  case "$1" in
    --root) (($# >= 2)) || die '--root requires a path'; ROOT="$2"; shift ;;
    --dest) (($# >= 2)) || die '--dest requires a path'; DEST="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'CAPO application installation requires Linux'
command -v cargo >/dev/null || die 'cargo is required; run install-os-packages.sh first'
command -v rustc >/dev/null || die 'rustc is required; run install-os-packages.sh first'
MANIFEST="$ROOT/runtime-daemon/Cargo.toml"
[[ -f "$MANIFEST" ]] || die 'runtime-daemon/Cargo.toml is missing'
grep -Eq '^name[[:space:]]*=[[:space:]]*"runtime-daemon"' "$MANIFEST" || die 'unexpected Runtime package name'

if [[ -f "$ROOT/runtime-daemon/Cargo.lock" ]]; then
  run cargo build --locked --release --manifest-path "$MANIFEST"
else
  printf 'Runtime has no committed Cargo.lock; building from Cargo.toml resolution.\n'
  run cargo build --release --manifest-path "$MANIFEST"
fi
SOURCE="$ROOT/runtime-daemon/target/release/runtime-daemon"
if ! "$DRY_RUN"; then [[ -x "$SOURCE" ]] || die 'Runtime release binary was not created'; fi
run install -d -m 0750 "$DEST"
run install -m 0755 "$SOURCE" "$DEST/runtime-daemon"

printf 'CAPO Runtime build and installation checks completed.\n'
