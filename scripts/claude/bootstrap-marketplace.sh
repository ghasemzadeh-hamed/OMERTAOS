#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: bootstrap-marketplace.sh [--install-plugins]

Ensures .claude/settings.json exists with the wshobson/agents marketplace and recommended plugins.

Options:
  --install-plugins  Attempt to install recommended plugins if Claude supports non-interactive mode.
  -h, --help         Show this help message.
USAGE
}

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd -- "$SCRIPT_DIR/../.." && pwd)
CLAUDE_DIR="$REPO_ROOT/.claude"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"

INSTALL_PLUGINS=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --install-plugins)
      INSTALL_PLUGINS=true
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

TEMPLATE_CONTENT=$(cat <<'JSON'
{
  "extraKnownMarketplaces": [
    "wshobson/agents"
  ],
  "enabledPlugins": {
    "python-development@wshobson/agents": true,
    "javascript-typescript@wshobson/agents": true,
    "backend-development@wshobson/agents": true,
    "kubernetes-operations@wshobson/agents": true,
    "cloud-infrastructure@wshobson/agents": true,
    "security-scanning@wshobson/agents": true,
    "code-review-ai@wshobson/agents": true,
    "full-stack-orchestration@wshobson/agents": true
  }
}
JSON
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
  echo "[warn] No JSON validator found (python/node). Skipping validation." >&2
  return 0
}

mkdir -p "$CLAUDE_DIR"

if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo "Creating $SETTINGS_FILE with marketplace defaults..."
  printf '%s\n' "$TEMPLATE_CONTENT" >"$SETTINGS_FILE"
else
  echo "Found existing $SETTINGS_FILE; leaving in place."
fi

if [[ -f "$SETTINGS_FILE" ]]; then
  if validate_json "$SETTINGS_FILE"; then
    echo "Settings JSON is valid."
  else
    echo "[error] $SETTINGS_FILE contains invalid JSON. Please fix before proceeding." >&2
    exit 2
  fi
fi

cat <<'INSTRUCTIONS'
Next steps (interactive inside Claude):
  /plugin marketplace add wshobson/agents
  /plugin install python-development@wshobson/agents
  /plugin install javascript-typescript@wshobson/agents
  /plugin install backend-development@wshobson/agents
  /plugin install kubernetes-operations@wshobson/agents
  /plugin install cloud-infrastructure@wshobson/agents
  /plugin install security-scanning@wshobson/agents
  /plugin install code-review-ai@wshobson/agents
  /plugin install full-stack-orchestration@wshobson/agents
INSTRUCTIONS

if $INSTALL_PLUGINS; then
  if command -v claude >/dev/null 2>&1; then
    echo "--install-plugins requested, but Claude Code currently requires an interactive TUI for plugin management."
    echo "Please open a terminal and run the commands above inside Claude."
  else
    echo "[warn] Claude is not installed. Install first, then run the commands above from within Claude."
  fi
fi
