#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: install-claude-code.sh [--dry-run]

Installs Claude Code using the official installer. Safe to re-run.

Options:
  --dry-run   Print the steps that would be executed without running them.
  -h, --help  Show this help message.
USAGE
}

DRY_RUN=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
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

if [[ $EUID -eq 0 ]]; then
  echo "[warn] Running as root. The installer usually runs as a regular user." >&2
fi

check_dep() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[error] Missing required dependency: $1" >&2
    exit 1
  fi
}

if command -v claude >/dev/null 2>&1; then
  CLAUDE_BIN=$(command -v claude)
  set +e
  CLAUDE_VERSION=$($CLAUDE_BIN --version 2>/dev/null)
  set -e
  echo "Claude Code already installed at $CLAUDE_BIN"
  [[ -n "${CLAUDE_VERSION:-}" ]] && echo "Version: $CLAUDE_VERSION"
  exit 0
fi

check_dep curl
check_dep bash

if $DRY_RUN; then
  cat <<'STEPS'
[dry-run] Claude Code not detected.
[dry-run] Would run: curl -fsSL https://claude.ai/install.sh | bash
[dry-run] Would verify that 'claude' is available on PATH after installation.
STEPS
  exit 0
fi

echo "Installing Claude Code via official installer..."
if ! curl -fsSL https://claude.ai/install.sh | bash; then
  echo "[error] Installation failed. Please check network connectivity and try again." >&2
  exit 1
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "[error] Claude binary not found after installation. Ensure ~/.local/bin or the install prefix is on PATH." >&2
  exit 1
fi

CLAUDE_BIN=$(command -v claude)
set +e
CLAUDE_VERSION=$($CLAUDE_BIN --version 2>/dev/null)
set -e

echo "Claude Code installed at $CLAUDE_BIN"
[[ -n "${CLAUDE_VERSION:-}" ]] && echo "Version: $CLAUDE_VERSION"
