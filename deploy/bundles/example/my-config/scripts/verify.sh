#!/usr/bin/env bash
set -euo pipefail
echo "[bundle] verifying deployment health"
curl -sf http://127.0.0.1:8001/api/health >/dev/null || exit 1
echo "[bundle] control plane healthy"
