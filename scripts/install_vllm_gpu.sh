#!/usr/bin/env bash
set -euo pipefail
# Helper to run vLLM via Docker.
# Requires the NVIDIA Container Toolkit and CUDA drivers.

MODEL_REPO="${1:-Qwen/Qwen2.5-7B-Instruct}"
TPORT="${2:-8008}"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found"
  exit 1
fi

if ! docker info | grep -q "Runtimes: nvidia"; then
  echo "NVIDIA Container Toolkit not detected in Docker info. Make sure it is installed."
fi

echo "Launching vLLM for $MODEL_REPO on port $TPORT ..."
docker run -d --restart unless-stopped \
  --gpus all \
  -p ${TPORT}:8000 \
  -e HF_TOKEN="${HF_TOKEN:-}" \
  -e VLLM_WORKER_USE_NCCL=0 \
  --name vllm \
  vllm/vllm-openai:latest \
  --model "$MODEL_REPO" \
  --dtype auto \
  --max-model-len 4096

echo "vLLM OpenAI-compatible server running on :$TPORT"
echo "Set models.local.engine=vllm and VLLM_HOST=http://localhost:${TPORT} in env/config."
