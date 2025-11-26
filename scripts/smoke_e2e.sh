#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

GATEWAY_PORT="${AION_GATEWAY_PORT:-8080}"
GATEWAY_URL="${NEXT_PUBLIC_GATEWAY_URL:-}"
if [[ -z "${GATEWAY_URL}" ]]; then
  GATEWAY_URL="http://localhost:${GATEWAY_PORT}"
elif [[ "${GATEWAY_URL}" =~ ^https?://(gateway|control|console|minio|postgres|redis|qdrant)(:|/|$) ]]; then
  GATEWAY_URL="http://localhost:${GATEWAY_PORT}"
fi
CONTROL_URL="${NEXT_PUBLIC_CONTROL_URL:-http://localhost:8000}"
CONSOLE_URL="${NEXTAUTH_URL:-http://localhost:3000}"
ADMIN_TOKEN="${AION_GATEWAY_ADMIN_TOKEN:-demo-admin-token}"

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

wait_for "control" "$CONTROL_URL/healthz"
wait_for "gateway" "$GATEWAY_URL/healthz"
wait_for "console" "$CONSOLE_URL/healthz"

curl -fsS "$CONSOLE_URL/dashboard/health/api" >/dev/null

if [[ -n "${ADMIN_TOKEN}" ]]; then
  curl -fsS -H "x-aion-admin-token: ${ADMIN_TOKEN}" "$GATEWAY_URL/healthz/auth" >/dev/null
fi

echo "All services healthy"
