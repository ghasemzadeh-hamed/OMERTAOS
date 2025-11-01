#!/usr/bin/env bash
set -euo pipefail

echo "[pre-apply] اجرای مهاجرت‌های پایگاه داده در حال انجام است..."
psql "$POSTGRES_URL" -c 'SELECT 1;' >/dev/null
