#!/usr/bin/env bash

echo "====================================="
echo "OMERTAOS Doctor"
echo "====================================="

check_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "$1: OK"
  else
    echo "$1: MISSING"
  fi
}

check_cmd git
check_cmd python3
check_cmd node
check_cmd npm
check_cmd docker
check_cmd cargo
check_cmd rg

echo ""
echo "Important OMERTAOS paths:"

for path in \
  "console" \
  "gateway" \
  "control" \
  "control-plane" \
  "runtime-daemon" \
  "rust-runtime" \
  "data" \
  "database" \
  "db" \
  "registry" \
  "models" \
  "schemas" \
  "policies" \
  "eventbus" \
  "observability" \
  "orchestration" \
  "integrations" \
  "execution" \
  "docker-compose.quickstart.yml" \
  "docker-compose.local.yml"
do
  if [ -e "$path" ]; then
    echo "OK: $path"
  else
    echo "MISSING: $path"
  fi
done
