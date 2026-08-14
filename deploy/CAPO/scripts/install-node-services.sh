#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
"$ROOT/deploy/native/scripts/install-gateway.sh" "$@"
exec "$ROOT/deploy/native/scripts/install-console.sh" "$@"
