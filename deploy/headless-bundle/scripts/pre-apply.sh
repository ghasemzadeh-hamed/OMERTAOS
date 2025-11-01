#!/usr/bin/env bash
set -euo pipefail

echo "[pre-apply] verifying database connectivity..."
psql "$POSTGRES_URL" -c 'SELECT 1;' >/dev/null
