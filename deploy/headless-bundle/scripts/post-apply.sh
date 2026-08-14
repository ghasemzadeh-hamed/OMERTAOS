#!/usr/bin/env bash
set -euo pipefail

echo "[post-apply] restarting core services"
systemctl restart aion-control.service aion-gateway.service aion-console.service
