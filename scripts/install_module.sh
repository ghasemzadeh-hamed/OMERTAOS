#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <module-ref> <destination-dir>" >&2
  exit 1
fi

MODULE_REF="$1"
DEST="$2"
COSIGN_KEY=${COSIGN_KEY:-"cosign.pub"}

mkdir -p "$DEST"

echo "Pulling module OCI artifact ${MODULE_REF}"
oras pull "$MODULE_REF" --output "$DEST"

if [[ -f "$COSIGN_KEY" ]]; then
  echo "Verifying signature"
  cosign verify --key "$COSIGN_KEY" "$MODULE_REF"
else
  echo "Warning: COSIGN_KEY not found, skipping verification" >&2
fi

if [[ -f "$DEST/manifest.yaml" ]]; then
  echo "Module manifest installed at $DEST"
else
  echo "Module manifest not found" >&2
  exit 2
fi
