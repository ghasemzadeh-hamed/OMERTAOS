#!/usr/bin/env bash
set -euo pipefail

MODEL_NAME="${1:-}"
TARGET_DIR="${LLM_HOME:-/tmp/aion/llms}"
REGISTRY_FILE="${TARGET_DIR}/registry.json"

if [[ -z "${MODEL_NAME}" ]]; then
  echo "usage: install_llm.sh <model_name>" >&2
  exit 1
fi

mkdir -p "${TARGET_DIR}"
MODEL_DIR="${TARGET_DIR}/${MODEL_NAME//\//_}"
mkdir -p "${MODEL_DIR}"

echo "{\"model\": \"${MODEL_NAME}\", \"installed_at\": \"$(date -u +%FT%TZ)\"}" > "${MODEL_DIR}/metadata.json"

export REGISTRY_FILE MODEL_DIR MODEL_NAME

python - <<'PY'
import json
import os
from pathlib import Path

registry = Path(os.environ["REGISTRY_FILE"])
registry.parent.mkdir(parents=True, exist_ok=True)
if registry.exists():
    payload = json.loads(registry.read_text())
else:
    payload = {"models": []}
entry = {"name": os.environ["MODEL_NAME"], "path": os.environ["MODEL_DIR"]}
if entry not in payload["models"]:
    payload["models"].append(entry)
registry.write_text(json.dumps(payload, indent=2))
PY

echo "Model ${MODEL_NAME} installed to ${MODEL_DIR}" >&2
