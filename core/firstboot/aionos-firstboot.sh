#!/usr/bin/env bash
set -euo pipefail
LOG_FILE=/var/log/aionos-firstboot.log
log() {
  local message="[firstboot] $*"
  echo "$message" | tee -a "$LOG_FILE"
}

load_profile_env() {
  local candidates=(/etc/aionos/profile.env /opt/aionos/.env /aionos/.env)
  for candidate in "${candidates[@]}"; do
    if [[ -f "$candidate" ]]; then
      # shellcheck disable=SC1090
      source "$candidate"
      log "loaded profile env from $candidate"
      return
    fi
  done
  log "no profile env detected; using defaults"
}

maybe_install() {
  if [[ $# -eq 0 ]]; then
    return
  fi
  if ! command -v apt-get >/dev/null 2>&1; then
    log "apt-get unavailable; skip install $*"
    return
  fi
  log "apt-get install $*"
  if ! DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"; then
    log "warn: failed to install $*"
  fi
}

maybe_enable_service() {
  local unit="$1"
  if ! command -v systemctl >/dev/null 2>&1; then
    return
  fi
  if systemctl list-unit-files "$unit" >/dev/null 2>&1; then
    if ! systemctl enable "$unit"; then
      log "warn: failed to enable $unit"
    fi
  fi
}

apply_hardening() {
  local level="${AION_HARDENING_LEVEL:-none}"
  case "$level" in
    cis-lite)
      log "hardening level cis-lite"
      maybe_install ufw auditd
      if command -v ufw >/dev/null 2>&1; then
        if ! ufw --force enable; then
          log "warn: ufw enable failed"
        fi
      fi
      maybe_enable_service auditd.service
      ;&
    standard)
      if [[ "$level" == "standard" ]]; then
        log "hardening level standard"
      fi
      maybe_install fail2ban
      if command -v systemctl >/dev/null 2>&1; then
        maybe_enable_service fail2ban.service
      fi
      ;;
    *)
      log "hardening level none"
      ;;
  esac
}

load_profile_env
PROFILE_NAME="${AION_PROFILE:-user}"
log "profile $PROFILE_NAME"

log "updates"
if ! apt-get update -y; then
  log "warn: apt-get update failed"
fi
if ! DEBIAN_FRONTEND=noninteractive apt-get upgrade -y; then
  log "warn: apt-get upgrade failed"
fi
if command -v snap >/dev/null 2>&1; then
  if ! snap refresh; then
    log "warn: snap refresh failed"
  fi
fi

log "drivers"
if lspci | grep -qi nvidia; then
  maybe_install ubuntu-drivers-common
  if ! ubuntu-drivers autoinstall; then
    log "warn: ubuntu-drivers autoinstall failed"
  fi
fi
maybe_install linux-firmware

log "services"
maybe_enable_service aionos.target

if [[ "${AION_DOCKER_ENABLED:-false}" == "true" ]]; then
  maybe_install docker.io docker-compose-plugin
  maybe_enable_service docker.service
fi

if [[ "${AION_JUPYTER_ENABLED:-false}" == "true" ]]; then
  maybe_install jupyter-notebook
  maybe_enable_service aionos-jupyter.service
fi

if [[ "${AION_MLFLOW_ENABLED:-false}" == "true" ]]; then
  maybe_install python3-mlflow
  maybe_enable_service aionos-mlflow.service
fi

if [[ "${AION_K8S_ENABLED:-false}" == "true" ]]; then
  maybe_install kubectl
fi

if [[ "${AION_LDAP_ENABLED:-false}" == "true" ]]; then
  maybe_install sssd
fi

apply_hardening

log "cleanup"
if ! apt-get autoremove -y; then
  log "warn: autoremove failed"
fi
rm -rf /var/cache/apt/archives/*.deb || true

log "done"
