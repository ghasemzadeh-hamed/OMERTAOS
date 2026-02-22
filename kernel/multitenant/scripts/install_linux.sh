#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v node >/dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
  sudo apt-get install -y nodejs
fi
sudo apt-get install -y python3-venv python3-pip

python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ./shared/control

pushd shared/gateway >/dev/null
npm i
popd >/dev/null

echo "OK. Use: scripts/run_all.sh PROFILE=user|pro|ent"
