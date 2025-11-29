#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

COMMON_LIB="${LIB_DIR}/common.sh"
ENV_LIB="${LIB_DIR}/env.sh"
CONFIG_LIB="${LIB_DIR}/config.sh"
DOCKER_LIB="${LIB_DIR}/docker.sh"
PREFLIGHT_LIB="${LIB_DIR}/preflight.sh"
CERTS_LIB="${LIB_DIR}/certs.sh"

for lib in "${COMMON_LIB}" "${ENV_LIB}" "${CONFIG_LIB}" "${DOCKER_LIB}" "${PREFLIGHT_LIB}" "${CERTS_LIB}"; do
  if [[ ! -f "${lib}" ]]; then
    echo "[ERROR] Required library '${lib}' is missing." >&2
    exit 1
  fi
done

# shellcheck source=lib/common.sh
source "${COMMON_LIB}"
# shellcheck source=lib/env.sh
source "${ENV_LIB}"
# shellcheck source=lib/config.sh
source "${CONFIG_LIB}"
# shellcheck source=lib/docker.sh
source "${DOCKER_LIB}"
# shellcheck source=lib/preflight.sh
source "${PREFLIGHT_LIB}"
# shellcheck source=lib/certs.sh
source "${CERTS_LIB}"

PROFILE=""
PROFILE_OPTION=""
NONINTERACTIVE=false
LOCAL_MODE=false
COMPOSE_FILE="docker-compose.yml"
MODEL_NAME="${AIONOS_LOCAL_MODEL:-llama3.2:3b}"
TELEMETRY_OPT_IN="$(normalize_boolean "${AION_TELEMETRY_OPT_IN:-false}")"
TELEMETRY_ENDPOINT="${AION_TELEMETRY_ENDPOINT:-http://localhost:4317}"
REPO_URL="${AIONOS_REPO_URL:-https://github.com/Hamedghz/OMERTAOS.git}"
BRANCH_NAME="${AIONOS_REPO_BRANCH:-main}"
UPDATE_REPO=false
POLICY_DIR="${AION_POLICY_DIR:-./policies}"
VOLUME_ROOT="${AION_VOLUME_ROOT:-./volumes}"
DEFAULT_DB_USER="aionos"
DEFAULT_DB_PASSWORD="password"
DEFAULT_DB_NAME="omerta_db"
DEFAULT_DATABASE_URL="postgresql://${DEFAULT_DB_USER}:${DEFAULT_DB_PASSWORD}@postgres:5432/${DEFAULT_DB_NAME}?schema=public"
DEFAULT_GATEWAY_API_KEYS="local-key:admin|manager"
GATEWAY_ADMIN_TOKEN="${AION_GATEWAY_ADMIN_TOKEN:-}"
ADMIN_TOKEN="${AION_ADMIN_TOKEN:-}"
GATEWAY_API_KEYS="${AION_GATEWAY_API_KEYS:-${DEFAULT_GATEWAY_API_KEYS}}"
NEXTAUTH_SECRET_VALUE="${NEXTAUTH_SECRET:-}"
CONSOLE_ADMIN_EMAIL="${CONSOLE_ADMIN_EMAIL:-admin@local}"
CONSOLE_ADMIN_PASSWORD="${CONSOLE_ADMIN_PASSWORD:-admin123}"
DATABASE_URL_VALUE="${DATABASE_URL:-${DEFAULT_DATABASE_URL}}"

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

generate_secret() {
  local bytes=${1:-32}
  python3 - <<PY
import secrets
print(secrets.token_urlsafe(${bytes}))
PY
}

prompt_value() {
  local prompt_label="$1"
  local default_value="$2"
  if ${NONINTERACTIVE}; then
    echo "${default_value}"
    return
  fi
  local input
  read -r -p "${prompt_label}" input || input="${default_value}"
  if [[ -z "${input}" ]]; then
    echo "${default_value}"
  else
    echo "${input}"
  fi
}

prompt_boolean() {
  local prompt_label="$1"
  local default_value="$2"
  if ${NONINTERACTIVE}; then
    echo "${default_value}"
    return
  fi
  local input
  read -r -p "${prompt_label}" input || input="${default_value}"
  input="${input:-${default_value}}"
  case "${input,,}" in
    y|yes|1|true|on) echo "true" ;;
    *) echo "false" ;;
  esac
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

collect_env_overrides() {
  if ${NONINTERACTIVE}; then
    [[ -z "${GATEWAY_ADMIN_TOKEN}" ]] && GATEWAY_ADMIN_TOKEN="$(generate_secret 32)"
    [[ -z "${ADMIN_TOKEN}" ]] && ADMIN_TOKEN="${GATEWAY_ADMIN_TOKEN}"
    [[ -z "${NEXTAUTH_SECRET_VALUE}" ]] && NEXTAUTH_SECRET_VALUE="$(generate_secret 48)"
    [[ -z "${GATEWAY_API_KEYS}" ]] && GATEWAY_API_KEYS="${DEFAULT_GATEWAY_API_KEYS}"
    TELEMETRY_OPT_IN=false
  else
    GATEWAY_ADMIN_TOKEN="$(prompt_value "Enter AION_GATEWAY_ADMIN_TOKEN (leave empty to auto-generate): " "${GATEWAY_ADMIN_TOKEN}")"
    if [[ -z "${GATEWAY_ADMIN_TOKEN}" ]]; then
      GATEWAY_ADMIN_TOKEN="$(generate_secret 32)"
    fi
    ADMIN_TOKEN="${GATEWAY_ADMIN_TOKEN}"

    GATEWAY_API_KEYS="$(prompt_value "Enter AION_GATEWAY_API_KEYS (format: key:role1|role2, default: ${DEFAULT_GATEWAY_API_KEYS}): " "${GATEWAY_API_KEYS}")"
    [[ -z "${GATEWAY_API_KEYS}" ]] && GATEWAY_API_KEYS="${DEFAULT_GATEWAY_API_KEYS}"

    NEXTAUTH_SECRET_VALUE="$(prompt_value "Enter NEXTAUTH_SECRET (leave empty to auto-generate): " "${NEXTAUTH_SECRET_VALUE}")"
    if [[ -z "${NEXTAUTH_SECRET_VALUE}" ]]; then
      NEXTAUTH_SECRET_VALUE="$(generate_secret 48)"
    fi

    TELEMETRY_OPT_IN="$(prompt_boolean "Allow anonymous telemetry? (y/N): " "false")"

    CONSOLE_ADMIN_EMAIL="$(prompt_value "Console admin email (default: ${CONSOLE_ADMIN_EMAIL}): " "${CONSOLE_ADMIN_EMAIL}")"
    CONSOLE_ADMIN_PASSWORD="$(prompt_value "Console admin password (default: ${CONSOLE_ADMIN_PASSWORD}): " "${CONSOLE_ADMIN_PASSWORD}")"
  fi

  [[ -z "${ADMIN_TOKEN}" ]] && ADMIN_TOKEN="${GATEWAY_ADMIN_TOKEN}"
  [[ -z "${CONSOLE_ADMIN_EMAIL}" ]] && CONSOLE_ADMIN_EMAIL="admin@local"
  [[ -z "${CONSOLE_ADMIN_PASSWORD}" ]] && CONSOLE_ADMIN_PASSWORD="admin123"
  [[ -z "${DATABASE_URL_VALUE}" ]] && DATABASE_URL_VALUE="${DEFAULT_DATABASE_URL}"
}

apply_env_overrides() {
  local env_file="${ROOT_DIR}/.env"
  env ENV_FILE="${env_file}" \
    PROFILE_VALUE="${PROFILE}" \
    FEATURE_SEAL_VALUE="$([[ "${PROFILE}" == "enterprise-vip" ]] && echo 1 || echo 0)" \
    TELEMETRY_VALUE="${TELEMETRY_OPT_IN}" \
    TELEMETRY_ENDPOINT_VALUE="${TELEMETRY_ENDPOINT}" \
    POLICY_DIR_VALUE="${POLICY_DIR}" \
    VOLUME_ROOT_VALUE="${VOLUME_ROOT}" \
    GATEWAY_PORT_VALUE="${AION_GATEWAY_PORT:-3000}" \
    GATEWAY_HOST_VALUE="${AION_GATEWAY_HOST:-0.0.0.0}" \
    PRISMA_VALUE="${AION_ENABLE_PRISMA:-1}" \
    DB_USER_VALUE="${DEFAULT_DB_USER}" \
    DB_PASSWORD_VALUE="${DEFAULT_DB_PASSWORD}" \
    DB_NAME_VALUE="${DEFAULT_DB_NAME}" \
    DATABASE_URL_VALUE_ENV="${DATABASE_URL_VALUE}" \
    REDIS_URL_VALUE="${AION_REDIS_URL:-redis://redis:6379/0}" \
    CONTROL_BASE_VALUE="${AION_CONTROL_BASE_URL:-http://control:8000}" \
    CONTROL_PREFIX_VALUE="${AION_CONTROL_API_PREFIX:-/api}" \
    CONTROL_GRPC_VALUE="${AION_CONTROL_GRPC:-http://control:50051}" \
    NEXTAUTH_SECRET_VALUE_ENV="${NEXTAUTH_SECRET_VALUE}" \
    GATEWAY_API_KEYS_VALUE="${GATEWAY_API_KEYS}" \
    GATEWAY_API_KEYS_SECRET_VALUE="${AION_GATEWAY_API_KEYS_SECRET_PATH:-}" \
    GATEWAY_ADMIN_TOKEN_VALUE="${GATEWAY_ADMIN_TOKEN}" \
    GATEWAY_ADMIN_TOKEN_SECRET_VALUE="${AION_GATEWAY_ADMIN_TOKEN_SECRET_PATH:-}" \
    ADMIN_TOKEN_VALUE="${ADMIN_TOKEN}" \
    ADMIN_TOKEN_SECRET_VALUE="${AION_ADMIN_TOKEN_SECRET_PATH:-}" \
    JWT_SECRET_PATH_VALUE="${AION_JWT_SECRET_PATH:-}" \
    SECRET_PROVIDER_MODE_VALUE="${SECRET_PROVIDER_MODE:-local}" \
    CONSOLE_ADMIN_EMAIL_VALUE="${CONSOLE_ADMIN_EMAIL}" \
    CONSOLE_ADMIN_PASSWORD_VALUE="${CONSOLE_ADMIN_PASSWORD}" \
    python3 - <<'PY'
from pathlib import Path
import os

env_path = Path(os.environ['ENV_FILE'])
lines = env_path.read_text().splitlines() if env_path.exists() else []

updates = {
    "AION_PROFILE": os.environ['PROFILE_VALUE'],
    "FEATURE_SEAL": os.environ['FEATURE_SEAL_VALUE'],
    "AION_TELEMETRY_OPT_IN": str(os.environ['TELEMETRY_VALUE']).lower() if str(os.environ['TELEMETRY_VALUE']).lower() in {'true', '1'} else 'false',
    "AION_TELEMETRY_ENDPOINT": os.environ['TELEMETRY_ENDPOINT_VALUE'],
    "AION_POLICY_DIR": os.environ['POLICY_DIR_VALUE'],
    "AION_VOLUME_ROOT": os.environ['VOLUME_ROOT_VALUE'],
    "AION_GATEWAY_PORT": os.environ['GATEWAY_PORT_VALUE'],
    "AION_GATEWAY_HOST": os.environ['GATEWAY_HOST_VALUE'],
    "AION_ENABLE_PRISMA": os.environ['PRISMA_VALUE'],
    "AION_DB_USER": os.environ['DB_USER_VALUE'],
    "AION_DB_PASSWORD": os.environ['DB_PASSWORD_VALUE'],
    "AION_DB_NAME": os.environ['DB_NAME_VALUE'],
    "DATABASE_URL": os.environ['DATABASE_URL_VALUE_ENV'],
    "AION_CONTROL_POSTGRES_DSN": os.environ['DATABASE_URL_VALUE_ENV'],
    "AION_REDIS_URL": os.environ['REDIS_URL_VALUE'],
    "CONTROL_BASE_URL": "http://localhost:8000",
    "GATEWAY_BASE_URL": "http://localhost:3000",
    "CONSOLE_BASE_URL": "http://localhost:3001",
    "AION_CONTROL_BASE_URL": os.environ['CONTROL_BASE_VALUE'],
    "AION_CONTROL_API_PREFIX": os.environ['CONTROL_PREFIX_VALUE'],
    "AION_CONTROL_GRPC": os.environ['CONTROL_GRPC_VALUE'],
    "NEXT_PUBLIC_GATEWAY_URL": "http://gateway:3000",
    "NEXTAUTH_URL": "http://localhost:3001",
    "NEXTAUTH_SECRET": os.environ['NEXTAUTH_SECRET_VALUE_ENV'],
    "AION_GATEWAY_API_KEYS": os.environ['GATEWAY_API_KEYS_VALUE'],
    "AION_GATEWAY_API_KEYS_SECRET_PATH": os.environ['GATEWAY_API_KEYS_SECRET_VALUE'],
    "AION_GATEWAY_ADMIN_TOKEN": os.environ['GATEWAY_ADMIN_TOKEN_VALUE'],
    "AION_GATEWAY_ADMIN_TOKEN_SECRET_PATH": os.environ['GATEWAY_ADMIN_TOKEN_SECRET_VALUE'],
    "AION_ADMIN_TOKEN": os.environ['ADMIN_TOKEN_VALUE'],
    "AION_ADMIN_TOKEN_SECRET_PATH": os.environ['ADMIN_TOKEN_SECRET_VALUE'],
    "AION_JWT_SECRET_PATH": os.environ['JWT_SECRET_PATH_VALUE'],
    "SECRET_PROVIDER_MODE": os.environ['SECRET_PROVIDER_MODE_VALUE'],
    "CONSOLE_ADMIN_EMAIL": os.environ['CONSOLE_ADMIN_EMAIL_VALUE'],
    "CONSOLE_ADMIN_PASSWORD": os.environ['CONSOLE_ADMIN_PASSWORD_VALUE'],
    "SKIP_CONSOLE_SEED": "false",
}

keys = set(updates)

def keep_line(line: str) -> bool:
    if not line or line.lstrip().startswith('#') or '=' not in line:
        return True
    key = line.split('=', 1)[0]
    return key not in keys

filtered = [line for line in lines if keep_line(line)]
filtered.extend(f"{key}={value}" for key, value in updates.items())
env_path.write_text("\n".join(filtered) + "\n")
PY
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

resolve_under_root() {
  local root_dir=$1
  local candidate=$2
  if [[ -z "${candidate}" ]]; then
    echo "${root_dir}"
    return
  fi
  if [[ "${candidate}" = /* ]]; then
    echo "${candidate}"
  else
    echo "${root_dir}/${candidate#./}"
  fi
}

prepare_runtime_paths() {
  local root_dir=$1
  local policy_dir=$2
  local volume_root=$3
  local policy_path
  local volume_path

  policy_path="$(resolve_under_root "${root_dir}" "${policy_dir}")"
  volume_path="$(resolve_under_root "${root_dir}" "${volume_root}")"

  ensure_directory "${policy_path}"
  ensure_directory "${volume_path}"
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

print_summary() {
  printf '\n[AION-OS] QuickSetup completed.\n'
  printf 'Profile: %s\n' "${PROFILE}"
  printf 'Compose file: %s\n' "${COMPOSE_FILE}"
  if ${LOCAL_MODE}; then
    printf 'Services:\n'
    printf '  Kernel API:       http://localhost:8010\n'
    printf '  Gateway (REST):   http://localhost:3000\n'
    printf '  Console UI:       http://localhost:3001\n'
  else
    printf 'Next steps:\n'
    local compose_display
    compose_display="$(compose_command_string 2>/dev/null || echo 'docker compose')"
    printf '  - Monitor stack: %s -f %s ps\n' "${compose_display}" "${COMPOSE_FILE}"
    printf '  - Smoke test: scripts/smoke_e2e.sh\n'
  fi
}

main() {
  parse_args "$@"
  ensure_prerequisites
  update_repository
  confirm_directory "${ROOT_DIR}"
  run_preflight "${ROOT_DIR}" "${NONINTERACTIVE}"
  ensure_env_file "${ROOT_DIR}"
  prepare_runtime_paths "${ROOT_DIR}" "${POLICY_DIR}" "${VOLUME_ROOT}"
  local policy_path
  local volume_path
  policy_path="$(resolve_under_root "${ROOT_DIR}" "${POLICY_DIR}")"
  volume_path="$(resolve_under_root "${ROOT_DIR}" "${VOLUME_ROOT}")"
  log_info "Policy directory: ${policy_path}"
  log_info "Volume root: ${volume_path}"
  select_profile
  log_info "Selected profile: ${PROFILE}"
  collect_env_overrides
  update_env_profile "${ROOT_DIR}" "${PROFILE}" "${TELEMETRY_OPT_IN}" "${TELEMETRY_ENDPOINT}" "${POLICY_DIR}" "${VOLUME_ROOT}"
  apply_env_overrides
  write_profile_metadata "${ROOT_DIR}" "${PROFILE}"
  ensure_config_file "${ROOT_DIR}" "${TELEMETRY_OPT_IN}" "${TELEMETRY_ENDPOINT}" "${POLICY_DIR}" "${VOLUME_ROOT}"
  ensure_ephemeral_certs "${ROOT_DIR}"
  if command_exists python3; then
    python3 "${SCRIPT_DIR}/generate_dev_certs.py" || log_warn "Development certificate generation failed"
  else
    log_warn "python3 not found; skipping development certificate generation"
  fi
  bring_up_stack "${ROOT_DIR}" "${COMPOSE_FILE}"
  install_ollama_model
  log_info "AION_GATEWAY_ADMIN_TOKEN=${GATEWAY_ADMIN_TOKEN}"
  log_info "AION_GATEWAY_API_KEYS=${GATEWAY_API_KEYS}"
  log_info "NEXTAUTH_URL=http://localhost:3000"
  log_info "NEXTAUTH_SECRET=${NEXTAUTH_SECRET_VALUE}"
  log_info "Console admin user: ${CONSOLE_ADMIN_EMAIL} / ${CONSOLE_ADMIN_PASSWORD}"
  print_summary
}

main "$@"
