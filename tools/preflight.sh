#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
ARGS=()
for arg in "$@"; do
  if [[ "$arg" == "--noninteractive" ]]; then
    ARGS+=("--noninteractive")
  fi
done
"${PYTHON}" "${SCRIPT_DIR}/preflight.py" "${ARGS[@]}"
