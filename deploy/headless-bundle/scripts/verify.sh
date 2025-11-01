#!/usr/bin/env bash
set -euo pipefail

echo "[verify] بررسی وضعیت سرویس‌ها"
aion doctor --verbose
curl -sf http://127.0.0.1:8001/api/health | jq .status
