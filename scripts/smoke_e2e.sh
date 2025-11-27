#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Load optional environment overrides when present
if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

# Base URLs with sensible defaults for local docker-compose usage
CONTROL_BASE_URL="${CONTROL_BASE_URL:-http://localhost:8000}"
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://localhost:8080}"
CONSOLE_BASE_URL="${CONSOLE_BASE_URL:-http://localhost:3000}"
ADMIN_TOKEN="${AION_GATEWAY_ADMIN_TOKEN:-demo-admin-token}"

wait_for() {
  local name=$1
  local url=$2
  echo "Waiting for $name at $url"
  for _ in $(seq 1 60); do
    if curl -fsS --max-time 5 "$url" >/dev/null; then
      echo "$name healthy"
      return 0
    fi
    sleep 5
  done
  echo "$name did not become ready" >&2
  return 1
}

# Authoritative health endpoints
wait_for "control" "$CONTROL_BASE_URL/healthz"
wait_for "gateway" "$GATEWAY_BASE_URL/healthz"
wait_for "console" "$CONSOLE_BASE_URL/healthz"

# Best-effort admin health (should not fail the smoke)
if [[ -n "${ADMIN_TOKEN}" ]]; then
  admin_status=$(curl -s -o /dev/null -w "%{http_code}" -H "x-aion-admin-token: ${ADMIN_TOKEN}" "$GATEWAY_BASE_URL/healthz/auth" || true)
  if [[ "$admin_status" == "200" ]]; then
    echo "gateway admin health responded 200"
  elif [[ "$admin_status" == "401" || "$admin_status" == "403" ]]; then
    echo "gateway admin health returned ${admin_status} (non-blocking)"
  elif [[ -n "$admin_status" ]]; then
    echo "gateway admin health returned $admin_status (non-blocking)"
  fi
fi

# Optional UI probe; accept common unauthenticated responses and downgrade others to warnings
ui_status=$(curl -s -o /dev/null -w "%{http_code}" "$CONSOLE_BASE_URL/login" || true)
if [[ "$ui_status" == "200" || "$ui_status" == "302" || "$ui_status" == "401" || "$ui_status" == "403" ]]; then
  echo "console UI reachable (status $ui_status)"
else
  echo "console UI returned $ui_status (non-blocking)"
fi

echo "All services healthy"
