#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"
COMMON_LIB="${LIB_DIR}/common.sh"

if [[ ! -f "${COMMON_LIB}" ]]; then
  echo "[ERROR] Required library '${COMMON_LIB}' is missing." >&2
  exit 1
fi

# shellcheck source=lib/common.sh
source "${COMMON_LIB}"

PROFILE=""
PROFILE_OPTION=""
NONINTERACTIVE=false
LOCAL_MODE=false
COMPOSE_FILE="docker-compose.yml"
MODEL_NAME="${AIONOS_LOCAL_MODEL:-llama3.2:3b}"
TELEMETRY_OPT_IN_RAW="${AION_TELEMETRY_OPT_IN:-false}"
TELEMETRY_ENDPOINT="${AION_TELEMETRY_ENDPOINT:-http://localhost:4317}"
REPO_URL="${AIONOS_REPO_URL:-https://github.com/ghasemzadeh-hamed/OMERTAOS.git}"
BRANCH_NAME="${AIONOS_REPO_BRANCH:-main}"
UPDATE_REPO=false

usage() {
  cat <<USAGE
Usage: $(basename "$0") [options]

Options:
  --profile <user|professional|enterprise>  Desired profile (default prompts interactively).
  --local                                   Use docker-compose.local.yml.
  --compose-file <path>                     Explicit docker compose file to use.
  --model <name>                            Ollama model to pull (default: ${MODEL_NAME}).
  --noninteractive                          Disable prompts; defaults apply.
  --update                                  Pull latest changes from the current Git branch.
  --repo <url>                              Repository URL when cloning is required.
  --branch <name>                           Branch to use when cloning or updating (default: ${BRANCH_NAME}).
  -h, --help                                Show this help message.
USAGE
}

normalize_profile() {
  local input="$1"
  case "${input,,}" in
    user|basic) echo "user" ;;
    professional|pro) echo "professional" ;;
    enterprise|enterprise-vip|enterprise_vip|enterprisevip) echo "enterprise-vip" ;;
    *)
      log_error "Unknown profile '${input}'. Expected user, professional, or enterprise."
      return 1
      ;;
  esac
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --profile)
        shift
        [[ $# -gt 0 ]] || { log_error "--profile requires an argument"; exit 1; }
        PROFILE_OPTION="$1"
        shift
        ;;
      --local)
        LOCAL_MODE=true
        COMPOSE_FILE="docker-compose.local.yml"
        shift
        ;;
      --compose-file)
        shift
        [[ $# -gt 0 ]] || { log_error "--compose-file requires an argument"; exit 1; }
        COMPOSE_FILE="$1"
        shift
        ;;
      --model)
        shift
        [[ $# -gt 0 ]] || { log_error "--model requires an argument"; exit 1; }
        MODEL_NAME="$1"
        shift
        ;;
      --noninteractive)
        NONINTERACTIVE=true
        shift
        ;;
      --update)
        UPDATE_REPO=true
        shift
        ;;
      --repo)
        shift
        [[ $# -gt 0 ]] || { log_error "--repo requires an argument"; exit 1; }
        REPO_URL="$1"
        shift
        ;;
      --branch)
        shift
        [[ $# -gt 0 ]] || { log_error "--branch requires an argument"; exit 1; }
        BRANCH_NAME="$1"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        log_error "Unknown argument: $1"
        usage
        exit 1
        ;;
    esac
  done
}

select_profile() {
  local default_choice="1"
  if [[ -n "${PROFILE_OPTION}" ]]; then
    PROFILE="$(normalize_profile "${PROFILE_OPTION}")"
    return
  fi

  if ${NONINTERACTIVE}; then
    if [[ -n "${AION_PROFILE:-}" ]]; then
      PROFILE="$(normalize_profile "${AION_PROFILE}")"
    elif [[ -n "${AION_PROFILE_CHOICE:-}" ]]; then
      case "${AION_PROFILE_CHOICE}" in
        2) PROFILE="professional" ;;
        3) PROFILE="enterprise-vip" ;;
        *) PROFILE="user" ;;
      esac
    else
      PROFILE="user"
    fi
    return
  fi

  printf '\nSelect AION-OS profile:\n'
  printf '  1) user           - Quickstart, local-only, minimal resources\n'
  printf '  2) professional   - Explorer + Terminal + IoT-ready\n'
  printf '  3) enterprise-vip - SEAL, GPU, advanced routing\n'
  read -r -p "Enter 1-3 [${default_choice}]: " selection || selection="${default_choice}"
  case "${selection}" in
    2) PROFILE="professional" ;;
    3) PROFILE="enterprise-vip" ;;
    *) PROFILE="user" ;;
  esac
}

ensure_prerequisites() {
  require_command git "Install Git from https://git-scm.com/downloads" || exit 1
  require_command docker "Install Docker Engine from https://docs.docker.com/engine/install/" || exit 1
  require_command python3 "Install Python 3.11+ from https://www.python.org/downloads/" || exit 1
  if ! command_exists curl && ! command_exists wget; then
    log_error "Either 'curl' or 'wget' is required for downloading dependencies."
    exit 1
  fi
}

compose_command=()

detect_compose() {
  if docker compose version >/dev/null 2>&1; then
    compose_command=(docker compose)
    return
  fi
  if command_exists docker-compose; then
    compose_command=(docker-compose)
    return
  fi
  log_error "Docker Compose v2 (docker compose) or v1 (docker-compose) is required."
  exit 1
}

update_repository() {
  if [[ -d "${ROOT_DIR}/.git" ]]; then
    if ${UPDATE_REPO}; then
      log_info "Updating repository (branch ${BRANCH_NAME})"
      (cd "${ROOT_DIR}" && git fetch --all && git checkout "${BRANCH_NAME}" && git pull --ff-only origin "${BRANCH_NAME}")
    fi
    return
  fi

  log_warn "No Git metadata found in ${ROOT_DIR}."
  local parent
  parent="$(dirname "${ROOT_DIR}")"
  local target="${parent}/OMERTAOS"
  if [[ "${ROOT_DIR}" == "${target}" ]]; then
    log_warn "Running from an archive or snapshot; skipping clone step."
    return
  fi
  log_info "Cloning repository into ${target}"
  git clone --branch "${BRANCH_NAME}" --single-branch "${REPO_URL}" "${target}"
  ROOT_DIR="$(cd "${target}" && pwd)"
}

ensure_env_file() {
  local env_file="${ROOT_DIR}/.env"
  local example_file="${ROOT_DIR}/config/templates/.env.example"
  if [[ ! -f "${env_file}" ]]; then
    if [[ -f "${example_file}" ]]; then
      log_info "Creating .env from template"
      cp "${example_file}" "${env_file}"
    else
      log_warn "No .env.example found; creating empty .env"
      touch "${env_file}"
    fi
  fi
}

update_env_profile() {
  local env_file="${ROOT_DIR}/.env"
  python3 - <<PY
from pathlib import Path
import os
from datetime import datetime

env_path = Path(${env_file!r})
lines = []
if env_path.exists():
    lines = [line.rstrip('\n') for line in env_path.read_text().splitlines()]

def keep_line(raw: str) -> bool:
    if not raw or raw.lstrip().startswith('#') or '=' not in raw:
        return True
    key, _ = raw.split('=', 1)
    return key not in {"AION_PROFILE", "FEATURE_SEAL", "AION_TELEMETRY_OPT_IN", "AION_TELEMETRY_ENDPOINT"}

filtered = [line for line in lines if keep_line(line)]

profile = ${PROFILE!r}
feature_seal = '1' if profile == 'enterprise-vip' else '0'
telemetry_raw = ${TELEMETRY_OPT_IN_RAW!r}
telemetry_value = str(telemetry_raw).lower() in {'1', 'true', 'y', 'yes'}
telemetry_endpoint = ${TELEMETRY_ENDPOINT!r}

filtered.extend([
    f"AION_PROFILE={profile}",
    f"FEATURE_SEAL={feature_seal}",
    f"AION_TELEMETRY_OPT_IN={'true' if telemetry_value else 'false'}",
    f"AION_TELEMETRY_ENDPOINT={telemetry_endpoint}",
])

env_path.write_text("\n".join(filtered) + "\n")
PY
}

write_profile_metadata() {
  local profile_dir="${ROOT_DIR}/.aionos"
  mkdir -p "${profile_dir}"
  python3 - <<PY
from pathlib import Path
from datetime import datetime
import json

profile_dir = Path(${profile_dir!r})
profile_dir.mkdir(parents=True, exist_ok=True)
profile_file = profile_dir / "profile.json"
data = {
    "profile": ${PROFILE!r},
    "setupDone": True,
    "updatedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
profile_file.write_text(json.dumps(data, indent=2) + "\n")
PY
}

ensure_config_file() {
  local config_dir="${ROOT_DIR}/config"
  local config_file="${config_dir}/aionos.config.yaml"
  mkdir -p "${config_dir}"
  if [[ -f "${config_file}" ]]; then
    return
  fi
  cat >"${config_file}" <<'YAML'
version: 1
locale: en-US
console:
  port: 3000
  baseUrl: http://localhost:3000
gateway:
  port: 8080
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
telemetry:
  otelEnabled: ${TELEMETRY_OPT_IN_RAW}
  endpoint: "${TELEMETRY_ENDPOINT}"
YAML
}

run_preflight() {
  local preflight="${ROOT_DIR}/tools/preflight.sh"
  if [[ -x "${preflight}" ]]; then
    log_info "Running preflight checks"
    if ${NONINTERACTIVE}; then
      "${preflight}" --noninteractive || log_warn "Preflight reported issues"
    else
      "${preflight}" || log_warn "Preflight reported issues"
    fi
  fi
}

install_ollama_model() {
  if [[ -z "${MODEL_NAME}" ]]; then
    return
  fi
  if command_exists ollama; then
    if ! ollama list | grep -q "${MODEL_NAME}"; then
      log_info "Pulling Ollama model ${MODEL_NAME}"
      if ! ollama pull "${MODEL_NAME}"; then
        log_warn "Ollama pull for ${MODEL_NAME} failed"
      fi
    fi
  else
    log_warn "Ollama CLI not found; skipping local model pull"
  fi
}

bring_up_stack() {
  detect_compose
  local compose_file_path="${ROOT_DIR}/${COMPOSE_FILE}"
  if [[ ! -f "${compose_file_path}" ]]; then
    log_error "Compose file '${COMPOSE_FILE}' not found in ${ROOT_DIR}."
    exit 1
  fi
  log_info "Starting services with ${compose_command[*]} -f ${COMPOSE_FILE} up -d --build"
  local attempt=1
  local max_attempts=3
  while (( attempt <= max_attempts )); do
    if (cd "${ROOT_DIR}" && "${compose_command[@]}" -f "${COMPOSE_FILE}" up -d --build); then
      return
    fi
    log_warn "docker compose attempt ${attempt}/${max_attempts} failed; retrying"
    sleep $((attempt * 5))
    attempt=$((attempt + 1))
  done
  log_error "docker compose failed after ${max_attempts} attempts"
  exit 1
}

print_summary() {
  printf '\n[AION-OS] QuickSetup completed.\n'
  printf 'Profile: %s\n' "${PROFILE}"
  printf 'Compose file: %s\n' "${COMPOSE_FILE}"
  if ${LOCAL_MODE}; then
    printf 'Services:\n'
    printf '  Kernel API:       http://localhost:8010\n'
    printf '  Gateway (REST):   http://localhost:8080\n'
    printf '  Console UI:       http://localhost:3000\n'
  else
    printf 'Next steps:\n'
    printf '  - Monitor stack: %s -f %s ps\n' "${compose_command[*]}" "${COMPOSE_FILE}"
    printf '  - Smoke test: scripts/smoke_e2e.sh\n'
  fi
}

main() {
  parse_args "$@"
  ensure_prerequisites
  update_repository
  confirm_directory "${ROOT_DIR}"
  run_preflight
  ensure_env_file
  select_profile
  log_info "Selected profile: ${PROFILE}"
  update_env_profile
  write_profile_metadata
  ensure_config_file
  bring_up_stack
  install_ollama_model
  print_summary
}

main "$@"
