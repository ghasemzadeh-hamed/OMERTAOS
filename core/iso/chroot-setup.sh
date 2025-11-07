#!/usr/bin/env bash
set -euo pipefail

# Helper script executed inside the live ISO chroot to perform additional
# provisioning steps that do not belong directly in build.sh. This can be sourced
# or executed with chroot once the base system is bootstrapped.

log() {
  printf '[chroot-setup] %s\n' "$*"
}

log "Updating package lists"
export DEBIAN_FRONTEND=noninteractive
apt-get update

log "Upgrading base system"
apt-get dist-upgrade -y

log "Cleaning up apt caches"
apt-get clean
rm -rf /var/lib/apt/lists/*

log "Chroot setup complete"
