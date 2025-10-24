#!/usr/bin/env bash
set -euo pipefail
IMAGE=${1:-ghcr.io/aionos/gateway:0.1.0}
KEY_PATH=${COSIGN_PUBLIC_KEY:-cosign.pub}

if ! command -v cosign >/dev/null 2>&1; then
  echo "cosign binary is required" >&2
  exit 1
fi

cosign verify --key "$KEY_PATH" "$IMAGE"
