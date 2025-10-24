#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <engine> <model> [--display <name>] [--privacy <policy>] [--intents intent1,intent2] [--endpoint <url>] [--policies <dir>]" >&2
  exit 1
fi

ENGINE="$1"
MODEL_ID="$2"
shift 2

DISPLAY_NAME="$MODEL_ID"
PRIVACY="local-only"
INTENTS=""
HEALTH_ENDPOINT=""
POLICY_DIR="policies"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --display)
      DISPLAY_NAME="$2"
      shift 2
      ;;
    --privacy)
      PRIVACY="$2"
      shift 2
      ;;
    --intents)
      INTENTS="$2"
      shift 2
      ;;
    --endpoint)
      HEALTH_ENDPOINT="$2"
      shift 2
      ;;
    --policies)
      POLICY_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

POLICY_FILE="$POLICY_DIR/models.yaml"
MODELS_ROOT=${MODELS_DIR:-"$POLICY_DIR/../data/models"}
TARGET_DIR="$MODELS_ROOT/$ENGINE/$MODEL_ID"

mkdir -p "$TARGET_DIR"

cat >"$TARGET_DIR/metadata.json" <<META
{
  "engine": "$ENGINE",
  "model": "$MODEL_ID",
  "installed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
META

echo "Model artifacts staged at $TARGET_DIR"

export POLICY_FILE="$POLICY_FILE"
export ENGINE
export MODEL_ID
export DISPLAY_NAME
export PRIVACY
export INTENTS
export HEALTH_ENDPOINT
export TARGET_DIR

python3 - <<'PY'
import os
from pathlib import Path
from typing import Any

import yaml

policy_file = Path(os.environ.get("POLICY_FILE", "policies/models.yaml"))
policy_dir = policy_file.parent
policy_dir.mkdir(parents=True, exist_ok=True)

if policy_file.exists():
    data: dict[str, Any] = yaml.safe_load(policy_file.read_text()) or {}
else:
    data = {}

defaults = data.setdefault("defaults", {})
defaults.setdefault("privacy", "local-only")
models = data.setdefault("models", [])

model_id = os.environ["MODEL_ID"]
engine = os.environ["ENGINE"]
display = os.environ["DISPLAY_NAME"]
privacy = os.environ["PRIVACY"]
intents = [i for i in os.environ.get("INTENTS", "").split(",") if i]
endpoint = os.environ.get("HEALTH_ENDPOINT", "")

existing = next((m for m in models if m.get("name") == model_id), None)
record = {
    "name": model_id,
    "display_name": display,
    "provider": engine,
    "mode": "local",
    "engine": "chat",
    "privacy": privacy,
    "intents": intents or ["general"],
    "latency_budget_ms": 1500,
    "metadata": {
        "engine": engine,
        "path": str(Path(os.environ["TARGET_DIR"]).resolve()),
    },
}
if endpoint:
    record["health"] = {"endpoint": endpoint, "method": "GET"}

if existing:
    models[models.index(existing)] = record
else:
    models.append(record)

policy_file.write_text(yaml.safe_dump(data, sort_keys=False))
print(f"Policy file updated: {policy_file}")
PY

