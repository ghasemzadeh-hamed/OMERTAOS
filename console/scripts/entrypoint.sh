#!/bin/sh
set -euo pipefail

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[console] DATABASE_URL is required" >&2
  exit 1
fi

PRISMA_BIN="./node_modules/.bin/prisma"

echo "[console] Applying database migrations..."
node "$PRISMA_BIN" migrate deploy

echo "[console] Bootstrapping console admin user..."
node ./scripts/dist/bootstrap-admin.js

echo "[console] Starting Next.js server..."
exec node node_modules/next/dist/bin/next start -p "${PORT:-3000}"
