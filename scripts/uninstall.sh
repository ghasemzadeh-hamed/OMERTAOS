#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

sudo systemctl disable --now aionos-console aionos-gateway aionos-control || true
sudo rm -f /etc/systemd/system/aionos-{console,gateway,control}.service
sudo systemctl daemon-reload

echo "Left repo at: $REPO_DIR (manual cleanup if needed)"
echo "Redis/PostgreSQL kept intact."
