#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Load optional environment overrides when present
if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

# Base URLs with sensible defaults aligned with docker-compose and dev.env
CONTROL_BASE_URL="${CONTROL_BASE_URL:-http://localhost:8000}"
GATEWAY_BASE_URL="${GATEWAY_BASE_URL:-http://localhost:8080}"
CONSOLE_BASE_URL="${CONSOLE_BASE_URL:-http://localhost:3000}"
ADMIN_TOKEN="${AION_GATEWAY_ADMIN_TOKEN:-demo-admin-token}"

SMOKE_RETRIES="${SMOKE_RETRIES:-120}"
SMOKE_DELAY="${SMOKE_DELAY:-3}"
SMOKE_HTTP_TIMEOUT="${SMOKE_HTTP_TIMEOUT:-5}"

print_diagnostics() {
  echo "[smoke_e2e] service readiness diagnostics:" >&2

  if command -v docker >/dev/null 2>&1; then
    echo "[smoke_e2e] docker compose ps:" >&2
    docker compose ps >&2 || true
    echo "[smoke_e2e] docker compose logs (tail=100):" >&2
    docker compose logs --tail=100 control gateway console >&2 || true
  fi

  for base in "$CONTROL_BASE_URL" "$GATEWAY_BASE_URL" "$CONSOLE_BASE_URL"; do
    echo "[smoke_e2e] curl -v $base" >&2
    curl -v --max-time "$SMOKE_HTTP_TIMEOUT" "$base" >/dev/null 2>&1 || true
  done
}

wait_for_any_endpoint() {
  local name=$1
  local base_url=$2
  shift 2
  local endpoints=("$@")

  echo "Waiting for $name at $base_url (${endpoints[*]})"
  for attempt in $(seq 1 "$SMOKE_RETRIES"); do
    for endpoint in "${endpoints[@]}"; do
      local url="${base_url%/}${endpoint}"
      if curl -fsS --max-time "$SMOKE_HTTP_TIMEOUT" "$url" >/dev/null; then
        echo "$name healthy via ${endpoint} (attempt ${attempt}/${SMOKE_RETRIES})"
        return 0
      fi
    done

    if (( attempt % 20 == 0 )); then
      echo "[smoke_e2e] still waiting for $name (${attempt}/${SMOKE_RETRIES})" >&2
    fi
    sleep "$SMOKE_DELAY"
  done

  echo "$name did not become ready after ${SMOKE_RETRIES} attempts" >&2
  return 1
}

trap 'print_diagnostics' ERR

# Authoritative health endpoints (accept /health, /ready fallbacks to avoid route drift)
wait_for_any_endpoint "control" "$CONTROL_BASE_URL" "/healthz" "/health" "/ready"
wait_for_any_endpoint "gateway" "$GATEWAY_BASE_URL" "/healthz" "/health" "/ready" "/readyz"
wait_for_any_endpoint "console" "$CONSOLE_BASE_URL" "/healthz" "/health" "/ready" "/readyz"

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
