#!/usr/bin/env bash
set -euo pipefail
echo "[AIONOS] native install"
command -v node >/dev/null || curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs
command -v pnpm >/dev/null || npm i -g pnpm

pnpm i
pnpm -C console build

# start console (systemd unit recommended in production)
echo "Run: pnpm -C console start"
