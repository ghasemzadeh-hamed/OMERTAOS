#!/usr/bin/env bash
set -euo pipefail
systemctl disable --now omertaos.service || true
rm -f /etc/systemd/system/omertaos.service
rm -rf /opt/omertaos
systemctl daemon-reload
