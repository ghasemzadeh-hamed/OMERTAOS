#!/usr/bin/env bash
# DEPRECATED: use scripts/quicksetup.sh instead of this installer.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "[WARN] scripts/install.sh is deprecated. Redirecting to scripts/quicksetup.sh." >&2
exec "${ROOT_DIR}/scripts/quicksetup.sh" "$@"
