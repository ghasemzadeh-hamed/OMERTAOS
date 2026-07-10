#!/bin/sh
set -eu

if [ -z "${DATABASE_URL:-}" ]; then
  echo "[console] DATABASE_URL is not set"
  exit 1
fi

echo "[console] Applying database migrations..."
./node_modules/.bin/prisma migrate deploy

echo "[console] Bootstrapping console admin user..."
node ./scripts/dist/bootstrap-admin.js || true

echo "[console] Starting Next.js server..."
exec node node_modules/next/dist/bin/next start -p "${PORT:-3000}"