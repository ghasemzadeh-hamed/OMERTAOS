#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../bridge-server"
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi
node dist/index.js
