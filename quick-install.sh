#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

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

DEV_ADMIN_EMAIL=${DEV_ADMIN_EMAIL:-dev-admin@aion.local}
DEV_ADMIN_PASSWORD=${DEV_ADMIN_PASSWORD:-$(python - <<'PY'
import secrets,string
alphabet=string.ascii_letters+string.digits
print(''.join(secrets.choice(alphabet) for _ in range(16)))
PY
)}
DEV_API_KEY=${DEV_API_KEY:-$(python - <<'PY'
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

append_if_missing "AION_GATEWAY_API_KEYS" "${DEV_API_KEY}:admin"
append_if_missing "AION_GATEWAY_ADMIN_TOKEN" "${AION_GATEWAY_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "AION_ADMIN_TOKEN" "${AION_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "AION_DEV_ADMIN_TOKEN" "${AION_DEV_ADMIN_TOKEN:-${DEV_API_KEY}}"
append_if_missing "DEV_ADMIN_EMAIL" "${DEV_ADMIN_EMAIL}"
append_if_missing "DEV_ADMIN_PASSWORD" "${DEV_ADMIN_PASSWORD}"
append_if_missing "DEV_API_KEY" "${DEV_API_KEY}"

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
