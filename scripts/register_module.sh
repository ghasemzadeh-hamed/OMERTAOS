#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <module-name> <module-path> <registry-ref>" >&2
  exit 1
fi

NAME="$1"
MODULE_PATH="$2"
REGISTRY_REF="$3"
COSIGN_KEY=${COSIGN_KEY:-"cosign.key"}

if [[ ! -d "$MODULE_PATH" ]]; then
  echo "Module path $MODULE_PATH not found" >&2
  exit 1
fi

oras push "$REGISTRY_REF/$NAME:latest" "$MODULE_PATH" --manifest-config /dev/null:application/vnd.aionos.config.v1+json
cosign sign --key "$COSIGN_KEY" "$REGISTRY_REF/$NAME:latest"

echo "Module $NAME published and signed"
