#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
cd "${ROOT_DIR}"

export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME:-omertaos}

if [ ! -f dev.env ]; then
  echo "dev.env missing; aborting." >&2
  exit 1
fi

if [ ! -f .env ]; then
  cp dev.env .env
  echo "Created .env from dev.env"
else
  cp .env .env.bak.$(date +%s)
  echo "Backed up existing .env"
fi

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "Python is required but was not found. Please install python3." >&2
    exit 1
  fi
fi

DEV_ADMIN_EMAIL=${DEV_ADMIN_EMAIL:-dev-admin@aion.local}
DEV_ADMIN_PASSWORD=${DEV_ADMIN_PASSWORD:-$($PYTHON_BIN - <<'PY'
import secrets,string
alphabet=string.ascii_letters+string.digits
print(''.join(secrets.choice(alphabet) for _ in range(16)))
PY
)}
DEV_API_KEY=${DEV_API_KEY:-$($PYTHON_BIN - <<'PY'
import secrets
print(secrets.token_hex(12))
PY
)}

append_if_missing() {
  local key="$1" value="$2"
  if ! grep -q "^${key}=" .env; then
    echo "${key}=${value}" >> .env
  fi
}

set_env() {
  local key="$1" value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s|^${key}=.*|${key}=${value}|" .env
  else
    echo "${key}=${value}" >> .env
  fi
}

append_if_missing "AION_GATEWAY_API_KEYS" "${DEV_API_KEY}:admin"
append_if_missing "AION_GATEWAY_ADMIN_TOKEN" "${AION_GATEWAY_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "AION_ADMIN_TOKEN" "${AION_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "AION_DEV_ADMIN_TOKEN" "${AION_DEV_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "DEV_ADMIN_EMAIL" "${DEV_ADMIN_EMAIL}"
append_if_missing "DEV_ADMIN_PASSWORD" "${DEV_ADMIN_PASSWORD}"
append_if_missing "DEV_API_KEY" "${DEV_API_KEY}"
append_if_missing "AION_GATEWAY_PORT" "8080"
append_if_missing "CONSOLE_PORT" "3000"

DB_USER=${AION_DB_USER:-aionos}
DB_PASSWORD=${AION_DB_PASSWORD:-password}
DB_NAME=${AION_DB_NAME:-omerta_db}
DB_HOST=${AION_DB_HOST:-postgres}
POSTGRES_DSN="postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?schema=public"

set_env "DATABASE_URL" "${POSTGRES_DSN}"
set_env "AION_CONTROL_POSTGRES_DSN" "${POSTGRES_DSN}"
set_env "CONSOLE_ADMIN_EMAIL" "${DEV_ADMIN_EMAIL}"
set_env "CONSOLE_ADMIN_PASSWORD" "${DEV_ADMIN_PASSWORD}"
set_env "AION_GATEWAY_API_KEYS" "${DEV_API_KEY}:admin"
set_env "AION_GATEWAY_ADMIN_TOKEN" "${AION_GATEWAY_ADMIN_TOKEN:-${DEV_API_KEY}}"
set_env "AION_ADMIN_TOKEN" "${AION_ADMIN_TOKEN:-${DEV_API_KEY}}"
set_env "AION_DEV_ADMIN_TOKEN" "${AION_DEV_ADMIN_TOKEN:-${DEV_API_KEY}}"
set_env "AION_DOCKER" "1"
set_env "AION_GATEWAY_PORT" "8080"
set_env "CONSOLE_PORT" "3000"
set_env "NEXTAUTH_URL" "http://localhost:3000"
set_env "NEXT_PUBLIC_GATEWAY_URL" "http://localhost:8080"

check_port() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn | awk '{print $4}' | grep -E "(^|:)${port}$" >/dev/null 2>&1
  elif command -v lsof >/dev/null 2>&1; then
    lsof -i tcp:"${port}" -sTCP:LISTEN >/dev/null 2>&1
  else
    return 1
  fi
}

for port in 3000 8080 8000; do
  if check_port "$port"; then
    echo "Port ${port} is already in use. Please free it before continuing." >&2
    exit 1
  fi
done

existing_stack="$(docker compose -f docker-compose.quickstart.yml ps -q || true)"
if [ -n "$existing_stack" ]; then
  echo "Stopping existing OMERTAOS stack..."
  docker compose -f docker-compose.quickstart.yml down -v
fi

echo "Generating self-signed certificates (dev only)..."
mkdir -p config/certs/dev config/keys
openssl req -x509 -newkey rsa:2048 -nodes -keyout config/certs/dev/dev.key -out config/certs/dev/dev.crt -days 365 -subj "/CN=localhost"
openssl genrsa -out config/keys/dev-jwt.key 2048
openssl rsa -in config/keys/dev-jwt.key -pubout -out config/keys/dev-jwt.pub

cat <<'NOTE'
WARNING: The generated certificates and keys are for development only.
Replace them with production-grade secrets and rotate any placeholder tokens
(DEV_SECRET_PLACEHOLDER) before deploying.
NOTE

echo "Starting stack with docker compose..."
docker compose -f docker-compose.quickstart.yml up --build -d

cat <<EOF

Quick install completed.
Services: control:8000, gateway:8080, console:3000

Dev credentials (for local/dev only):
  Email:    ${DEV_ADMIN_EMAIL}
  Password: ${DEV_ADMIN_PASSWORD}
  API key:  ${DEV_API_KEY}

You can re-run this bootstrap safely via: make bootstrap
EOF
