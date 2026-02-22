#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "${ROOT_DIR}"

log() {
  echo "[verify] $1"
}

run_step() {
  local description="$1"
  shift
  log "${description}"
  "$@"
}

if command -v python >/dev/null 2>&1; then
  run_step "Upgrade pip" python -m pip install --upgrade pip
  run_step "Install Python dependencies" python -m pip install -r requirements.txt
  if [ -f "pyproject.toml" ]; then
    run_step "Install project editable extras" python -m pip install -e .[dev]
  fi
  if command -v pre-commit >/dev/null 2>&1; then
    run_step "Run pre-commit" pre-commit run --all-files
  else
    log "pre-commit not installed; installing" && python -m pip install pre-commit
    run_step "Run pre-commit" pre-commit run --all-files
  fi
  if command -v pytest >/dev/null 2>&1; then
    run_step "Run pytest" pytest -q
  fi
else
  echo "Python is required for verification" >&2
  exit 1
fi

if [ -d "gateway" ]; then
  run_step "Install gateway dependencies" npm ci --prefix gateway
  run_step "Lint gateway" npm run lint --prefix gateway --if-present
  run_step "Test gateway" npm test --prefix gateway --if-present -- --watch=false
fi

if [ -d "console" ]; then
  run_step "Install console dependencies" npm ci --prefix console
  run_step "Lint console" npm run lint --prefix console --if-present
  run_step "Build console" npm run build --prefix console --if-present
fi

log "Verification completed"
