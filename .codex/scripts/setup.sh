#!/usr/bin/env bash
set -e

echo "====================================="
echo "OMERTAOS Native Setup"
echo "====================================="

echo "Current branch:"
git branch --show-current || true

mkdir -p logs tmp .cache/tmp storage/backups storage/exports storage/imports

if [ -f "requirements.txt" ]; then
  if [ ! -d ".venv" ]; then
    python3 -m venv .venv
  fi

  . .venv/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
fi

for dir in console gateway; do
  if [ -f "$dir/package.json" ]; then
    echo "Installing Node dependencies in $dir"
    cd "$dir"
    if [ -f "package-lock.json" ]; then
      npm ci
    else
      npm install
    fi
    cd -
  fi
done

if command -v docker >/dev/null 2>&1 && [ -f "docker-compose.quickstart.yml" ]; then
  docker compose -f docker-compose.quickstart.yml config >/dev/null || true
fi

echo "Native setup completed."
echo "No long-running service was started."
