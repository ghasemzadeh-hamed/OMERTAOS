#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-llama3.2:3b}"
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

# نصب Ollama (Linux/macOS). روی Windows WSL هم پاسخ می‌دهد.
if [ "$OLLAMA_HOST" = "http://127.0.0.1:11434" ]; then
  if ! command -v ollama >/dev/null 2>&1; then
    echo "Installing Ollama ..."
    curl -fsSL https://ollama.com/install.sh | sh
  fi

  # اجرا
  if pgrep -x "ollama" >/dev/null 2>&1; then
    echo "Ollama is already running."
  else
    echo "Starting ollama serve ..."
    nohup ollama serve >/tmp/ollama.log 2>&1 &
    sleep 2
  fi
else
  echo "Detected remote/custom OLLAMA_HOST=$OLLAMA_HOST — skipping local install/start."
  if ! command -v ollama >/dev/null 2>&1; then
    echo "ollama CLI not found; install it manually if you want to manage remote models."
    exit 0
  fi
fi

echo "Pulling model: $MODEL via $OLLAMA_HOST"
OLLAMA_HOST="$OLLAMA_HOST" ollama pull "$MODEL" || true

echo "✅ Local LLM ready via Ollama → $MODEL"
