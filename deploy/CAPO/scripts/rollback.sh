#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
usage() {
  printf '%s\n' \
    'Usage: rollback.sh [--dry-run] [--help]' \
    'Stop and disable CAPO units without deleting configuration, data, accounts, or source.'
}
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'native rollback requires Linux'
command -v systemctl >/dev/null || die 'systemctl is required'
if ((EUID == 0)); then PRIV=(); else command -v sudo >/dev/null || die 'run as root or install sudo'; PRIV=(sudo); fi

run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "${PRIV[@]}" "$@"; printf '\n';
  else "${PRIV[@]}" "$@"; fi
}

run systemctl stop omertaos.target
run systemctl disable omertaos.target
run systemctl daemon-reload
printf '%s\n' 'CAPO units stopped and disabled. Persistent state and configuration were preserved.'
