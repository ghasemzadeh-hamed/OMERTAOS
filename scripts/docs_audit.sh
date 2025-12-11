#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOC_FILE="${ROOT_DIR}/docs/audit/source-of-truth.md"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.yml"
ENV_FILE="${ROOT_DIR}/dev.env"
README_FILE="${ROOT_DIR}/README.md"

failures=0

require_file() {
  local path="$1"
  if [[ ! -f "$path" ]]; then
    echo "[docs-audit] Missing required file: $path" >&2
    failures=$((failures+1))
  fi
}

require_file "$DOC_FILE"
require_file "$COMPOSE_FILE"
require_file "$ENV_FILE"
require_file "$README_FILE"

# Extract host ports from compose (numeric tokens before ':').
if [[ -f "$COMPOSE_FILE" ]]; then
  mapfile -t compose_ports < <(python - <<'PY'
import re, pathlib
text = pathlib.Path("docker-compose.yml").read_text()
ports = sorted({m.group(1) for m in re.finditer(r'"?(\d+):', text)})
for p in ports:
    print(p)
PY
  )
  for port in "${compose_ports[@]}"; do
    if ! grep -q "${port}" "$DOC_FILE"; then
      echo "[docs-audit] Port ${port} missing from ${DOC_FILE}" >&2
      failures=$((failures+1))
    fi
  done
fi

# Ensure every non-empty env var in dev.env is referenced in the source-of-truth doc.
if [[ -f "$ENV_FILE" ]]; then
  while IFS= read -r line; do
    [[ -z "$line" || "$line" =~ ^# ]] && continue
    key="${line%%=*}"
    if ! grep -q "${key}" "$DOC_FILE"; then
      echo "[docs-audit] Environment key ${key} missing from ${DOC_FILE}" >&2
      failures=$((failures+1))
    fi
  done < "$ENV_FILE"
fi

# Verify README mentions the quick-install entry point.
if ! grep -q "quick-install.sh" "$README_FILE"; then
  echo "[docs-audit] README missing quick-install reference" >&2
  failures=$((failures+1))
fi

if [[ $failures -gt 0 ]]; then
  echo "[docs-audit] Found ${failures} documentation drift issue(s)." >&2
  exit 1
fi

echo "[docs-audit] Documentation is in sync with compose and dev.env."
