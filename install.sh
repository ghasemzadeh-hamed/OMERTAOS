#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEFAULT_PROFILE="quickstart"
PROFILE="${1:-$DEFAULT_PROFILE}"

case "$PROFILE" in
  quickstart)
    echo "Running quickstart environment setup..."
    export AION_WITH_BIGDATA="false"
    ;;
  bigdata)
    echo "Running quickstart environment with big data services..."
    export AION_WITH_BIGDATA="true"
    ;;
  *)
    echo "Unknown profile: $PROFILE" >&2
    echo "Supported profiles: quickstart (default), bigdata" >&2
    exit 1
    ;;
esac

"$SCRIPT_DIR/scripts/dev-up.sh"
