#!/usr/bin/env bash
set -euo pipefail
install -d /opt/omertaos/bin
cp infra/linux/start.sh /opt/omertaos/bin/start.sh
chmod +x /opt/omertaos/bin/start.sh
cp infra/linux/omertaos.service /etc/systemd/system/omertaos.service
systemctl daemon-reload
systemctl enable omertaos.service
