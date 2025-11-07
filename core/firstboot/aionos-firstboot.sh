#!/usr/bin/env bash
set -euo pipefail

LOG="/var/log/aionos-firstboot.log"
exec > >(tee -a "$LOG") 2>&1

log() {
  printf '[aionos-firstboot] %s\n' "$*"
}

run_as_aionos() {
  su - aionos -c "$1"
}

log "Starting AIONOS first boot provisioning"

export DEBIAN_FRONTEND=noninteractive
apt-get update || true

# Detect GPUs and install vendor drivers when possible.
if lspci | grep -qi nvidia; then
  log "NVIDIA GPU detected"
  apt-get install -y nvidia-driver-535 || apt-get install -y nvidia-driver || true
fi

if lspci | grep -qi 'amd/ati'; then
  log "AMD GPU detected"
  apt-get install -y firmware-amd-graphics || true
fi

# Ensure the latest firmware bundle is present.
apt-get install -y linux-firmware || true

# Prepare OMERTAOS stack if it was baked into the image.
if [ -d /opt/omertaos ]; then
  log "Configuring OMERTAOS stack"
  chown -R aionos:aionos /opt/omertaos || true

  if [ -f /opt/omertaos/requirements.txt ]; then
    log "Installing Python dependencies"
    python3 -m pip install --upgrade pip || true
    python3 -m pip install -r /opt/omertaos/requirements.txt || true
  fi

  if [ -d /opt/omertaos/control ]; then
    log "Setting up control service virtual environment"
    python3 -m pip install -e /opt/omertaos || true
  fi

  if [ -d /opt/omertaos/gateway ]; then
    log "Installing gateway Node.js dependencies"
    run_as_aionos 'cd /opt/omertaos/gateway && npm install --omit=dev && npm run build'
  fi

  if [ -d /opt/omertaos/console ]; then
    log "Installing console Node.js dependencies"
    run_as_aionos 'cd /opt/omertaos/console && npm install --omit=dev && npm run build'
  fi

  systemctl enable aionos-gateway.service || true
  systemctl enable aionos-control.service || true
  systemctl enable aionos-console.service || true
  systemctl enable aionos.target || true
fi

log "AIONOS first boot provisioning complete"
