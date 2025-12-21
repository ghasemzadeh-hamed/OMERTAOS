#!/usr/bin/env bash
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "${ROOT_DIR}"

if command -v docker >/dev/null 2>&1; then
  :
else
  echo "docker is required for doctor checks" >&2
  exit 1
fi

if [ -f .env ]; then
  # shellcheck disable=SC2046
  set -a && source .env && set +a
fi

COMPOSE="docker compose -f docker-compose.quickstart.yml"
GATEWAY_HOST=${GATEWAY_BASE_URL:-${AION_GATEWAY_URL:-${NEXT_PUBLIC_GATEWAY_URL:-http://localhost:8080}}}
CONTROL_HOST=${CONTROL_BASE_URL:-http://localhost:8000}
CONSOLE_HOST=${CONSOLE_BASE_URL:-${NEXTAUTH_URL:-http://localhost:3000}}

status=0

print_section() {
  echo ""
  echo "== $1 =="
}

check_console_db() {
  print_section "Console database configuration"
  if ! db_url=$(${COMPOSE} exec -T console sh -c 'printf "%s" "${DATABASE_URL}"' 2>/dev/null); then
    echo "Failed to read DATABASE_URL from console container"
    status=1
    return
  fi

  if [ -z "$db_url" ]; then
    echo "DATABASE_URL is not set inside the console container"
    status=1
    return
  fi

  provider="unknown"
  case "$db_url" in
    postgres*|POSTGRES*) provider="postgresql" ;;
    file:*) provider="sqlite" ;;
  esac
  redacted=$(echo "$db_url" | sed 's#://[^:/]*:[^@]*@#://***:***@#')
  echo "Provider: $provider"
  echo "URL: $redacted"

  diag_response=$(curl -fsS "${CONSOLE_HOST}/api/system/database" 2>/dev/null || true)
  if [ -n "$diag_response" ]; then
    echo "Console reported: $diag_response"
  fi
}

check_gateway_profile() {
  print_section "Gateway profile API"
  api_key=${DEV_API_KEY:-${AION_DEV_ADMIN_TOKEN:-${AION_GATEWAY_ADMIN_TOKEN:-}}}
  if [ -z "$api_key" ]; then
    echo "DEV_API_KEY or AION_DEV_ADMIN_TOKEN is not set; cannot query gateway profile"
    status=1
    return
  fi

  if ! profile_payload=$(curl -fsS -H "x-api-key: ${api_key}" "${GATEWAY_HOST}/v1/config/profile" 2>/dev/null); then
    echo "Failed to fetch /v1/config/profile with the dev API key"
    status=1
    return
  fi

  echo "Profile payload: $profile_payload"
}

check_control_health() {
  print_section "Control health"
  if ! health_payload=$(curl -fsS "${CONTROL_HOST}/healthz" 2>/dev/null); then
    echo "Control health check failed"
    status=1
    return
  fi
  echo "Health response: $health_payload"
}

check_console_db
check_gateway_profile
check_control_health

if [ "$status" -ne 0 ]; then
  echo "\nDoctor detected issues." >&2
else
  echo "\nDoctor checks passed."
fi

exit "$status"
