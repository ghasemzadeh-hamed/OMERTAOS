#!/usr/bin/env bash
set -euo pipefail
"$(dirname "$0")"/../deploy/ci/verify.sh "$@"
