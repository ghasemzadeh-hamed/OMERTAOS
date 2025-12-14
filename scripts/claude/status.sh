#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
SETTINGS_FILE="$REPO_ROOT/.claude/settings.json"
OUTPUT_JSON=false

usage() {
  cat <<'USAGE'
Usage: status.sh [--json]

Reports Claude Code installation and marketplace bootstrap status.

Options:
  --json   Emit machine-readable JSON.
  -h, --help  Show this help message.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      OUTPUT_JSON=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

RECOMMENDED_PLUGINS=(
  "python-development@wshobson/agents"
  "javascript-typescript@wshobson/agents"
  "backend-development@wshobson/agents"
  "kubernetes-operations@wshobson/agents"
  "cloud-infrastructure@wshobson/agents"
  "security-scanning@wshobson/agents"
  "code-review-ai@wshobson/agents"
  "full-stack-orchestration@wshobson/agents"
)

validate_json() {
  if command -v python >/dev/null 2>&1; then
    python -m json.tool "$1" >/dev/null 2>&1 && return 0 || return 1
  fi
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool "$1" >/dev/null 2>&1 && return 0 || return 1
  fi
  if command -v node >/dev/null 2>&1; then
    node -e "JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8'));" "$1" >/dev/null 2>&1 && return 0 || return 1
  fi
  return 0
}

json_escape() {
  local raw="$1"
  raw=${raw//\\/\\\\}
  raw=${raw//\"/\\\"}
  raw=${raw//$'\n'/ }
  printf '%s' "$raw"
}

CLAUDE_INSTALLED=false
CLAUDE_PATH=""
CLAUDE_VERSION=""
if command -v claude >/dev/null 2>&1; then
  CLAUDE_INSTALLED=true
  CLAUDE_PATH=$(command -v claude)
  set +e
  CLAUDE_VERSION=$($CLAUDE_PATH --version 2>/dev/null)
  set -e
fi

SETTINGS_PRESENT=false
SETTINGS_VALID=false
SETTINGS_ERROR=""
if [[ -f "$SETTINGS_FILE" ]]; then
  SETTINGS_PRESENT=true
  if validate_json "$SETTINGS_FILE"; then
    SETTINGS_VALID=true
  else
    SETTINGS_ERROR="Invalid JSON"
  fi
else
  SETTINGS_ERROR="Missing settings file"
fi

EXIT_CODE=0
if ! $CLAUDE_INSTALLED || ! $SETTINGS_PRESENT; then
  EXIT_CODE=1
fi
if [[ -n "$SETTINGS_ERROR" && "$SETTINGS_ERROR" != "Missing settings file" ]]; then
  EXIT_CODE=2
fi

if $OUTPUT_JSON; then
  escaped_path=$(json_escape "$CLAUDE_PATH")
  escaped_version=$(json_escape "$CLAUDE_VERSION")
  escaped_error=$(json_escape "$SETTINGS_ERROR")
  escaped_settings_file=$(json_escape "$SETTINGS_FILE")
  escaped_repo_root=$(json_escape "$REPO_ROOT")
  printf '{"claude":{"installed":%s,"path":"%s","version":"%s"},"settings":{"present":%s,"valid":%s,"error":"%s"},"recommendedPlugins":[' \
    "$CLAUDE_INSTALLED" "$escaped_path" "$escaped_version" "$SETTINGS_PRESENT" "$SETTINGS_VALID" "$escaped_error"
  for ((i=0; i<${#RECOMMENDED_PLUGINS[@]}; i++)); do
    plugin=${RECOMMENDED_PLUGINS[$i]}
    if [[ $i -gt 0 ]]; then printf ','; fi
    printf '"%s"' "$plugin"
  done
  printf '],"settingsFile":"%s","repoRoot":"%s"}\n' "$escaped_settings_file" "$escaped_repo_root"
else
  echo "Claude installed: $CLAUDE_INSTALLED"
  [[ -n "$CLAUDE_PATH" ]] && echo "Binary path: $CLAUDE_PATH"
  [[ -n "$CLAUDE_VERSION" ]] && echo "Version: $CLAUDE_VERSION"
  echo "Settings file present: $SETTINGS_PRESENT"
  echo "Settings valid JSON: $SETTINGS_VALID"
  [[ -n "$SETTINGS_ERROR" ]] && echo "Settings note: $SETTINGS_ERROR"
  echo "Recommended plugins:"
  for plugin in "${RECOMMENDED_PLUGINS[@]}"; do
    echo "  - $plugin"
  done
fi

exit $EXIT_CODE
