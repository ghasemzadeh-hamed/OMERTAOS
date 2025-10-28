#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(cd "$SCRIPT_DIR/.." && pwd)

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required" >&2
  exit 1
fi

if [[ ! -f "$ROOT_DIR/.env" && -f "$ROOT_DIR/.env.example" ]]; then
  echo "Creating default .env from .env.example"
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi

if [[ ! -f "$ROOT_DIR/bigdata/.env" && -f "$ROOT_DIR/bigdata/.env.example" ]]; then
  echo "Creating default bigdata/.env from bigdata/.env.example"
  cp "$ROOT_DIR/bigdata/.env.example" "$ROOT_DIR/bigdata/.env"
fi

COMPOSE_ARGS=("-f" "$ROOT_DIR/docker-compose.yml")

if [[ "${AION_WITH_BIGDATA:-false}" == "true" ]]; then
  COMPOSE_ARGS+=("-f" "$ROOT_DIR/bigdata/docker-compose.bigdata.yml")
fi

pushd "$ROOT_DIR" >/dev/null
  docker compose "${COMPOSE_ARGS[@]}" up -d
popd >/dev/null

echo "Gateway available at http://localhost:${AION_GATEWAY_PORT:-8080}"
echo "Console available at http://localhost:3000"
