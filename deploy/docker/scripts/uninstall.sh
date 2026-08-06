#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "${SCRIPT_DIR}/../../.." && pwd)
COMPOSE_FILE="$REPO_ROOT/deploy/docker/compose/full.yml"
if [ -f "$COMPOSE_FILE" ]; then
  cd "$REPO_ROOT"
else
  echo "Could not locate deploy/docker/compose/full.yml." >&2
  exit 1
fi

echo "Stopping and removing AION-OS Docker stack..."
docker compose --project-directory . -f "$COMPOSE_FILE" down -v
echo "AION-OS stack down and volumes removed."
