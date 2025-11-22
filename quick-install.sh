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

echo "Quick install completed. Services: control:8000, gateway:8080, console:3000"
