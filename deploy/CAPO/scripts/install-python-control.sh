#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=false
ROOT="${OMERTAOS_ROOT:-/opt/omertaos/OMERTAOS}"
VENV="${OMERTAOS_CONTROL_VENV:-/var/lib/omertaos/venvs/control}"

usage() {
  cat <<'EOF'
Usage: install-python-control.sh [--root PATH] [--venv PATH] [--dry-run] [--help]

Create or update the CAPO Control virtual environment from the repository
pyproject.toml and verify the canonical control.app.main:app entrypoint.
EOF
}

die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
run() {
  if "$DRY_RUN"; then printf 'DRY-RUN:'; printf ' %q' "$@"; printf '\n'; else "$@"; fi
}

while (($#)); do
  case "$1" in
    --root) (($# >= 2)) || die '--root requires a path'; ROOT="$2"; shift ;;
    --venv) (($# >= 2)) || die '--venv requires a path'; VENV="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $1" ;;
  esac
  shift
done

[[ "$(uname -s)" == Linux ]] || die 'CAPO application installation requires Linux'
command -v python3 >/dev/null || die 'python3 is required; run install-os-packages.sh first'
[[ -f "$ROOT/pyproject.toml" ]] || die "missing $ROOT/pyproject.toml"
[[ -f "$ROOT/control/app/main.py" ]] || die 'canonical Control entrypoint is missing'

if [[ ! -x "$VENV/bin/python" ]]; then
  run mkdir -p "$(dirname "$VENV")"
  run python3 -m venv "$VENV"
fi

run "$VENV/bin/python" -m pip install --disable-pip-version-check -e "$ROOT[control]"
if ! "$DRY_RUN"; then
  "$VENV/bin/python" -c 'from control.app.main import app; assert app is not None'
  "$VENV/bin/python" -c 'import fastapi, uvicorn; print("Control dependencies and entrypoint: OK")'
fi

printf 'CAPO Control installation checks completed.\n'
