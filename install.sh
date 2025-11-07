#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
CONFIG_DIR="${ROOT_DIR}/config"
CONFIG_FILE="${CONFIG_DIR}/aionos.config.yaml"
MODEL_NAME="${AIONOS_LOCAL_MODEL:-llama3.2:3b}"
TELEMETRY_OPT_IN_RAW="${AION_TELEMETRY_OPT_IN:-false}"
TELEMETRY_OPT_IN="$(printf '%s' "${TELEMETRY_OPT_IN_RAW}" | tr '[:upper:]' '[:lower:]')"
if [[ "${TELEMETRY_OPT_IN}" == "true" || "${TELEMETRY_OPT_IN}" == "1" ]]; then
  TELEMETRY_ENABLED_VALUE=true
else
  TELEMETRY_ENABLED_VALUE=false
fi
TELEMETRY_ENDPOINT="${AION_TELEMETRY_ENDPOINT:-http://localhost:4317}"
NONINTERACTIVE=false
COMPOSE_FILE="docker-compose.yml"
LOCAL_MODE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local)
      LOCAL_MODE=true
      COMPOSE_FILE="docker-compose.local.yml"
      shift
      ;;
    --noninteractive)
      NONINTERACTIVE=true
      shift
      ;;
    --model)
      shift
      MODEL_NAME="$1"
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

cd "$ROOT_DIR"

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "Expected compose file '$COMPOSE_FILE' was not found." >&2
  exit 1
fi

if [[ -x "${TOOLS_DIR}/preflight.sh" ]]; then
  if $NONINTERACTIVE; then
    "${TOOLS_DIR}/preflight.sh" --noninteractive
  else
    "${TOOLS_DIR}/preflight.sh"
  fi
fi

if [[ ! -f .env && -f config/templates/.env.example ]]; then
  cp config/templates/.env.example .env
fi

if ! $NONINTERACTIVE; then
  echo ""
  echo "Select AION-OS kernel profile:"
  echo "  1) user           - Quickstart, local-only, minimal resources"
  echo "  2) professional   - Explorer + Terminal + IoT-ready"
  echo "  3) enterprise-vip - SEAL, GPU, advanced routing"
  read -r -p "Enter 1-3 [1]: " PROFILE_CHOICE || PROFILE_CHOICE=""
else
  PROFILE_CHOICE=${AION_PROFILE_CHOICE:-1}
fi

case "${PROFILE_CHOICE}" in
  2) AION_PROFILE="professional" ;;
  3) AION_PROFILE="enterprise-vip" ;;
  *) AION_PROFILE="user" ;;
esac

if [[ ! -f .env ]]; then
  touch .env
fi

sed -i.bak '/^AION_PROFILE=/d' .env 2>/dev/null || true
sed -i.bak '/^FEATURE_SEAL=/d' .env 2>/dev/null || true
rm -f .env.bak

if [[ "${AION_PROFILE}" == "enterprise-vip" ]]; then
  {
    echo "AION_PROFILE=enterprise-vip"
    echo "FEATURE_SEAL=1"
  } >> .env
else
  {
    echo "AION_PROFILE=${AION_PROFILE}"
    echo "FEATURE_SEAL=0"
  } >> .env
fi

PROFILE_DIR="${ROOT_DIR}/.aionos"
mkdir -p "${PROFILE_DIR}"
cat > "${PROFILE_DIR}/profile.json" <<JSON
{
  "profile": "${AION_PROFILE}",
  "setupDone": true,
  "updatedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
JSON

echo "Selected kernel profile: ${AION_PROFILE}"

mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_FILE" ]]; then
  cat > "$CONFIG_FILE" <<YAML
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
  otelEnabled: ${TELEMETRY_ENABLED_VALUE}
  endpoint: "${TELEMETRY_ENDPOINT}"
YAML
fi

ensure_compose() {
  local attempt=1
  local max_attempts=3
  while (( attempt <= max_attempts )); do
    if docker compose -f "$COMPOSE_FILE" up -d --build; then
      return 0
    fi
    echo "docker compose failed (attempt ${attempt}/${max_attempts}); retrying..." >&2
    sleep $((attempt * 5))
    attempt=$((attempt + 1))
  done
  echo "docker compose failed after ${max_attempts} attempts" >&2
  return 1
}

install_ollama_model() {
  if command -v ollama >/dev/null 2>&1; then
    if ollama --version >/dev/null 2>&1; then
      if ! ollama list | grep -q "${MODEL_NAME}"; then
        if ! ollama pull "${MODEL_NAME}"; then
          echo "Warning: ollama pull ${MODEL_NAME} failed" >&2
        fi
      fi
    fi
  else
    echo "Ollama not installed; skipping local model pull" >&2
  fi
}

ensure_compose
install_ollama_model

if [[ -x scripts/install_local_llm.sh ]]; then
  chmod +x scripts/install_local_llm.sh scripts/install_vllm_gpu.sh scripts/smoke_e2e.sh >/dev/null 2>&1 || true
fi

if ! $NONINTERACTIVE; then
  if $LOCAL_MODE; then
    cat <<MSG
OMERTAOS personal stack installation complete.
To launch the stack:
  docker compose -f docker-compose.local.yml up -d

Personal mode services:
  Kernel API:       http://localhost:8010
  Gateway (REST):   http://localhost:8080
  Console UI:       http://localhost:3000
MSG
  else
    cat <<MSG
OMERTAOS installation complete.
To launch the stack:
  docker compose up -d

Run the smoke test:
  scripts/smoke_e2e.sh
MSG
  fi
fi
