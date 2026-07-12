#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
UNIT_SOURCE="$(cd -- "$SCRIPT_DIR/../systemd" && pwd)"
UNIT_DEST=/etc/systemd/system

usage() {
  cat <<'EOF'
Usage: setup-systemd.sh [--dry-run] [--help]

Install the reviewed CAPO units, reload systemd, and enable omertaos.target.
This does not start services and preserves the operator-owned environment file.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n';
  else "$@"; fi
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'systemd setup requires Linux'
command -v systemctl >/dev/null || die 'systemctl is required'
if ((EUID == 0)); then PRIV=(); else command -v sudo >/dev/null || die 'run as root or install sudo'; PRIV=(sudo); fi
id omertaos >/dev/null 2>&1 || die 'service account omertaos is missing; run install-os-packages.sh first'
[[ -f /etc/omertaos/omertaos.env ]] || die 'create and secure /etc/omertaos/omertaos.env first'

units=(omertaos-runtime.service omertaos-control.service omertaos-gateway.service omertaos-console.service omertaos.target)
for unit in "${units[@]}"; do
  [[ -f "$UNIT_SOURCE/$unit" ]] || die "missing unit source: $unit"
  run "${PRIV[@]}" install -o root -g root -m 0644 "$UNIT_SOURCE/$unit" "$UNIT_DEST/$unit"
done
run "${PRIV[@]}" systemctl daemon-reload
run "${PRIV[@]}" systemctl enable omertaos.target
printf 'CAPO systemd units installed and enabled; services were not started.\n'
