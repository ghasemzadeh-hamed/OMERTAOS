#!/usr/bin/env bash
# shellcheck shell=bash

# Configuration helpers for QuickSetup.

ensure_config_file() {
  local root_dir=$1
  local telemetry_enabled=$2
  local telemetry_endpoint=$3
  local config_dir="${root_dir}/config"
  local config_file="${config_dir}/aionos.config.yaml"

  mkdir -p "${config_dir}"

  if [[ -f "${config_file}" ]]; then
    return
  fi

  cat >"${config_file}" <<YAML
version: 1
locale: en-US
console:
  port: 3000
  baseUrl: http://localhost:3000
gateway:
  port: 8080
  host: localhost
  apiKeys:
    - demo-key:admin|manager
control:
  httpPort: 8000
  grpcPort: 50051
storage:
  postgres:
    host: postgres
    port: 5432
    user: aion
    password: aion
    database: aion
  redis:
    host: redis
    port: 6379
  qdrant:
    host: qdrant
    port: 6333
  minio:
    endpoint: http://minio:9000
    accessKey: minio
    secretKey: miniosecret
    bucket: aion-raw
policies:
  dir: ./policies
volumes:
  root: ./volumes
telemetry:
  otelEnabled: ${telemetry_enabled}
  endpoint: "${telemetry_endpoint}"
YAML

  log_info "Created default configuration at ${config_file}"
}
