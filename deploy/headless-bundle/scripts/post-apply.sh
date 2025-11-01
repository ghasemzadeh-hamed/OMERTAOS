#!/usr/bin/env bash
set -euo pipefail

echo "[post-apply] راه‌اندازی مجدد سرویس‌ها"
systemctl restart aion-control.service aion-gateway.service aion-console.service
