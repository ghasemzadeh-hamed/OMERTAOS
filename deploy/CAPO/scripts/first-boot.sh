#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
START=false
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
usage() {
  cat <<'EOF'
Usage: first-boot.sh [--dry-run] [--start] [--help]

Run the idempotent CAPO installers in order and install systemd units. Services
remain stopped unless --start is explicitly supplied.
EOF
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
while (($#)); do case "$1" in --dry-run) DRY_RUN=true;; --start) START=true;; --help|-h) usage; exit 0;; *) die "unknown argument: $1";; esac; shift; done
[[ "$(uname -s)" == Linux ]] || die 'first boot requires Linux'
args=(); "$DRY_RUN" && args+=(--dry-run)
for installer in install-os-packages.sh install-data-services.sh install-python-control.sh install-node-services.sh install-rust-runtime.sh setup-systemd.sh; do
  [[ -x "$SCRIPT_DIR/$installer" ]] || die "missing executable installer: $installer"
  "$SCRIPT_DIR/$installer" "${args[@]}"
done
if "$START"; then "$SCRIPT_DIR/run-all.sh" "${args[@]}"; else printf 'CAPO installation complete; services remain stopped.\n'; fi
