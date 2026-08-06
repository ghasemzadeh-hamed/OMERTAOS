#!/usr/bin/env bash
set -euo pipefail
DRY_RUN=false
usage() { printf 'Usage: run.sh [--dry-run] [--help]\nStart the native OMERTAOS systemd target after N6 validation.\n'; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
while (($#)); do case "$1" in --dry-run) DRY_RUN=true;; --help|-h) usage; exit 0;; *) die "unknown argument: $1";; esac; shift; done
[[ "$(uname -s)" == Linux ]] || die 'service lifecycle requires Linux'
command -v systemctl >/dev/null || die 'systemctl is required'
if ((EUID == 0)); then PRIV=(); else command -v sudo >/dev/null || die 'run as root or install sudo'; PRIV=(sudo); fi
systemctl is-enabled --quiet omertaos.target || die 'omertaos.target is not enabled; complete N6 first'
if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "${PRIV[@]}" systemctl start omertaos.target; printf '\n'
else
  "${PRIV[@]}" systemctl start omertaos.target
  "${PRIV[@]}" systemctl is-active --quiet omertaos.target || die 'omertaos.target did not become active'
fi
