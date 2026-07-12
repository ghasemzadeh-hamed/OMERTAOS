#!/usr/bin/env bash
set -euo pipefail
DRY_RUN=false
usage() { printf 'Usage: stop-all.sh [--dry-run] [--help]\nStop the native OMERTAOS target without touching persistent data.\n'; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
while (($#)); do case "$1" in --dry-run) DRY_RUN=true;; --help|-h) usage; exit 0;; *) die "unknown argument: $1";; esac; shift; done
[[ "$(uname -s)" == Linux ]] || die 'service lifecycle requires Linux'
command -v systemctl >/dev/null || die 'systemctl is required'
if ((EUID == 0)); then PRIV=(); else command -v sudo >/dev/null || die 'run as root or install sudo'; PRIV=(sudo); fi
if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "${PRIV[@]}" systemctl stop omertaos.target; printf '\n'; else "${PRIV[@]}" systemctl stop omertaos.target; fi
