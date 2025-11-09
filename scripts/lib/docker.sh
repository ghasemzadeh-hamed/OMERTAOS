#!/usr/bin/env bash
# shellcheck shell=bash

# Docker compose helpers shared across setup scripts.

declare -a COMPOSE_CMD=()

detect_compose() {
  if [[ ${#COMPOSE_CMD[@]} -gt 0 ]]; then
    return
  fi

  if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD=(docker compose)
    return
  fi

  if command_exists docker-compose; then
    COMPOSE_CMD=(docker-compose)
    return
  fi

  log_error "Docker Compose v2 (docker compose) or v1 (docker-compose) is required."
  return 1
}

compose_command_string() {
  if [[ ${#COMPOSE_CMD[@]} -eq 0 ]]; then
    detect_compose || return 1
  fi
  printf '%s' "${COMPOSE_CMD[*]}"
}

bring_up_stack() {
  local root_dir=$1
  local compose_file=$2
  local attempts=${3:-3}

  detect_compose || return 1

  local compose_path="${root_dir}/${compose_file}"
  if [[ ! -f "${compose_path}" ]]; then
    log_error "Compose file '${compose_file}' not found in ${root_dir}."
    return 1
  fi

  log_info "Starting services with ${COMPOSE_CMD[*]} -f ${compose_file} up -d --build"

  local attempt=1
  while (( attempt <= attempts )); do
    if (cd "${root_dir}" && "${COMPOSE_CMD[@]}" -f "${compose_file}" up -d --build); then
      return 0
    fi
    log_warn "docker compose attempt ${attempt}/${attempts} failed; retrying"
    sleep $((attempt * 5))
    attempt=$((attempt + 1))
  done

  log_error "docker compose failed after ${attempts} attempts"
  return 1
}
