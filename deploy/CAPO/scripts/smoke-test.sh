#!/usr/bin/env bash
set -euo pipefail

MODE=native
TIMEOUT=5

usage() {
  printf '%s\n' \
    'Usage: smoke-test.sh [--mode native|quickstart] [--timeout SECONDS] [--help]' \
    'Read-only readiness checks for Console, Gateway, Control, and Runtime.'
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
pass() { printf 'PASS: %s\n' "$*"; }

while (($#)); do
  case "$1" in
    --mode) [[ $# -ge 2 ]] || die '--mode requires a value'; MODE="$2"; shift ;;
    --timeout) [[ $# -ge 2 ]] || die '--timeout requires a value'; TIMEOUT="$2"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$MODE" == native || "$MODE" == quickstart ]] || die 'mode must be native or quickstart'
[[ "$TIMEOUT" =~ ^[1-9][0-9]*$ ]] || die 'timeout must be a positive integer'
command -v curl >/dev/null || die 'curl is required'

check_http() {
  local name="$1" url="$2"
  curl --fail --silent --show-error --max-time "$TIMEOUT" "$url" >/dev/null
  pass "$name ($url)"
}

check_http Control http://127.0.0.1:8000/health
check_http Gateway http://127.0.0.1:8080/health
check_http Console http://127.0.0.1:3000/

if [[ "$MODE" == native ]]; then
  [[ "$(uname -s)" == Linux ]] || die 'native Runtime readiness requires Linux'
  command -v systemctl >/dev/null || die 'systemctl is required for native readiness'
  systemctl is-active --quiet omertaos-runtime.service
  pass 'Runtime systemd service'
  systemctl is-active --quiet omertaos.target
  pass 'OMERTAOS target'
else
  command -v docker >/dev/null || die 'docker is required for Quickstart readiness'
  docker compose -f docker-compose.quickstart.yml ps --status running runtime | grep -q runtime
  pass 'Runtime Quickstart container'
fi

printf 'CAPO %s smoke test passed.\n' "$MODE"
