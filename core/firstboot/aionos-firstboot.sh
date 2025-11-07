#!/usr/bin/env bash
set -euo pipefail
log(){ echo "[firstboot] $*" | tee -a /var/log/aionos-firstboot.log; }

log "updates..."
apt-get update -y || true
apt-get upgrade -y || true
command -v snap >/dev/null && snap refresh || true

log "drivers..."
if lspci | grep -qi nvidia; then apt-get install -y nvidia-driver || true; fi
apt-get install -y linux-firmware || true

log "enable services..."
systemctl enable aionos.target || true

log "cleanup..."
apt-get autoremove -y || true
rm -rf /var/cache/apt/archives/*.deb || true

log "done"
