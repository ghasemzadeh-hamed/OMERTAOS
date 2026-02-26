#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/../.." && pwd)
if [ -f "$REPO_ROOT/docker-compose.yml" ]; then
  cd "$REPO_ROOT"
else
  echo "Could not locate docker-compose.yml. Run this script from the repository root or alongside it." >&2
  exit 1
fi

echo "Stopping and removing AION-OS Docker stack..."
docker compose down -v
echo "AION-OS stack down and volumes removed."
