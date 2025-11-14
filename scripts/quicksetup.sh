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
REPO_URL="${AIONOS_REPO_URL:-https://github.com/ghasemzadeh-hamed/OMERTAOS.git}"
BRANCH_NAME="${AIONOS_REPO_BRANCH:-main}"
UPDATE_REPO=false
POLICY_DIR="${AION_POLICY_DIR:-./policies}"
VOLUME_ROOT="${AION_VOLUME_ROOT:-./volumes}"

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
    printf '  Gateway (REST):   http://localhost:8080\n'
    printf '  Console UI:       http://localhost:3000\n'
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
  update_env_profile "${ROOT_DIR}" "${PROFILE}" "${TELEMETRY_OPT_IN}" "${TELEMETRY_ENDPOINT}" "${POLICY_DIR}" "${VOLUME_ROOT}"
  write_profile_metadata "${ROOT_DIR}" "${PROFILE}"
  ensure_config_file "${ROOT_DIR}" "${TELEMETRY_OPT_IN}" "${TELEMETRY_ENDPOINT}" "${POLICY_DIR}" "${VOLUME_ROOT}"
  ensure_ephemeral_certs "${ROOT_DIR}"
  bring_up_stack "${ROOT_DIR}" "${COMPOSE_FILE}"
  install_ollama_model
  print_summary
}

main "$@"
