#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLS_DIR="${ROOT_DIR}/tools"
CONFIG_DIR="${ROOT_DIR}/config"
CONFIG_FILE="${CONFIG_DIR}/aionos.config.yaml"
MODEL_NAME="${AIONOS_LOCAL_MODEL:-llama3.2:3b}"
NONINTERACTIVE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
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

if [[ -x "${TOOLS_DIR}/preflight.sh" ]]; then
  if $NONINTERACTIVE; then
    "${TOOLS_DIR}/preflight.sh" --noninteractive
  else
    "${TOOLS_DIR}/preflight.sh"
  fi
fi

if [[ ! -f .env && -f .env.example ]]; then
  cp .env.example .env
fi

mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_FILE" ]]; then
  cat > "$CONFIG_FILE" <<'YAML'
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
  otelEnabled: false
  endpoint: http://localhost:4317
YAML
fi

ensure_compose() {
  local attempt=1
  local max_attempts=3
  while (( attempt <= max_attempts )); do
    if docker compose up -d --build; then
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
  cat <<MSG
OMERTAOS installation complete.
To launch the stack:
  docker compose up -d

Run the smoke test:
  scripts/smoke_e2e.sh
MSG
fi
