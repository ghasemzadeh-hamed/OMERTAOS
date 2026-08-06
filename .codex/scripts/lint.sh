#!/usr/bin/env bash
set -uo pipefail

echo "Running OMERTAOS lint checks..."

failures=()

run_check() {
  local name="$1"
  shift
  echo
  echo "==> $name"
  if "$@"; then
    echo "PASSED: $name"
  else
    local exit_code=$?
    echo "FAILED: $name (exit $exit_code)" >&2
    failures+=("$name")
  fi
}

python_cmd=()
if [ -x ".venv/bin/python" ]; then
  python_cmd=(".venv/bin/python")
elif command -v python3 >/dev/null 2>&1 && python3 -c "import sys" >/dev/null 2>&1; then
  python_cmd=("python3")
elif command -v python >/dev/null 2>&1 && python -c "import sys" >/dev/null 2>&1; then
  python_cmd=("python")
elif command -v py >/dev/null 2>&1 && py -3 -c "import sys" >/dev/null 2>&1; then
  python_cmd=("py" "-3")
fi

if command -v ruff >/dev/null 2>&1; then
  run_check "Python Ruff" ruff check .
elif [ "${#python_cmd[@]}" -gt 0 ]; then
  run_check "Python compile" "${python_cmd[@]}" -m compileall -q \
    control data policies eventbus observability orchestration
fi

if command -v npm >/dev/null 2>&1; then
  if [ -f "gateway/package.json" ]; then
    run_check "Gateway ESLint" npm run lint --prefix gateway --if-present
  fi
  if [ -f "console/package.json" ]; then
    run_check "Console lint" npm run lint --prefix console --if-present
  fi
fi

if command -v cargo >/dev/null 2>&1 && [ -f "runtime-daemon/Cargo.toml" ]; then
  run_check "Runtime rustfmt" \
    cargo fmt --manifest-path runtime-daemon/Cargo.toml -- --check
fi

if [ "${#failures[@]}" -gt 0 ]; then
  printf '\nLint failures: %s\n' "${failures[*]}" >&2
  exit 1
fi

echo
echo "All available OMERTAOS lint checks passed."
