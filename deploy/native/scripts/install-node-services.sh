#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
"$SCRIPT_DIR/install-gateway.sh" "$@"
exec "$SCRIPT_DIR/install-console.sh" "$@"
