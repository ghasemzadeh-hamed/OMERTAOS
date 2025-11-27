#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

CONTROL_PORT="${AION_CONTROL_PORT:-8000}"
GATEWAY_PORT="${AION_GATEWAY_PORT:-8080}"
CONTROL_BASE_URL="${CONTROL_BASE_URL:-${NEXT_PUBLIC_CONTROL_URL:-http://localhost:${CONTROL_PORT}}}"
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-${NEXT_PUBLIC_GATEWAY_URL:-http://localhost:${GATEWAY_PORT}}}"
CONSOLE_URL="${NEXTAUTH_URL:-http://localhost:3000}"
ADMIN_TOKEN="${AION_GATEWAY_ADMIN_TOKEN:-demo-admin-token}"

normalize_to_local() {
  local url=$1
  local host=$2
  local port=$3
  if [[ "$url" =~ ^https?://${host}(:|/|$) ]]; then
    echo "http://localhost:${port}"
  else
    echo "$url"
  fi
}

CONTROL_BASE_URL=$(normalize_to_local "$CONTROL_BASE_URL" "control" "$CONTROL_PORT")
GATEWAY_BASE_URL=$(normalize_to_local "$GATEWAY_BASE_URL" "gateway" "$GATEWAY_PORT")

wait_for() {
  local name=$1
  local url=$2
  echo "Waiting for $name at $url"
  for i in {1..60}; do
    if curl -fsS "$url" >/dev/null; then
      echo "$name healthy"
      return 0
    fi
    sleep 5
  done
  echo "$name did not become ready" >&2
  return 1
}

wait_for "control" "$CONTROL_BASE_URL/healthz"
wait_for "gateway" "$GATEWAY_BASE_URL/healthz"
wait_for "console" "$CONSOLE_URL/healthz"

curl -fsS "$CONSOLE_URL/dashboard/health/api" >/dev/null

if [[ -n "${ADMIN_TOKEN}" ]]; then
  curl -fsS -H "x-aion-admin-token: ${ADMIN_TOKEN}" "$GATEWAY_BASE_URL/healthz/auth" >/dev/null
fi

echo "All services healthy"
