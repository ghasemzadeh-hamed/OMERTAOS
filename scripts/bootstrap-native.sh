#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "[bootstrap-native] please run as root (e.g. sudo bash scripts/bootstrap-native.sh)" >&2
  exit 1
fi

TARGET_USER=${SUDO_USER:-$(logname 2>/dev/null || echo root)}
TARGET_HOME=$(eval echo "~${TARGET_USER}")
if [[ ! -d "${TARGET_HOME}" ]]; then
  echo "[bootstrap-native] could not resolve home directory for ${TARGET_USER}" >&2
  exit 1
fi

USER_PATH="${TARGET_HOME}/.local/bin:${TARGET_HOME}/.cargo/bin:/usr/local/bin:/usr/bin:/bin"

run_as_user() {
  local cmd="$1"
  if command -v sudo >/dev/null 2>&1; then
    sudo -u "${TARGET_USER}" -H env PATH="${USER_PATH}" HOME="${TARGET_HOME}" bash -lc "$cmd"
  else
    runuser -u "${TARGET_USER}" -- env PATH="${USER_PATH}" HOME="${TARGET_HOME}" bash -lc "$cmd"
  fi
}

apt-get update
apt-get install -y git curl build-essential python3.11-venv python3-pip \
  redis-server postgresql postgresql-contrib pkg-config libssl-dev libpq-dev cmake

if ! command -v node >/dev/null 2>&1 || ! node --version | grep -q '^v20'; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

if ! command -v pnpm >/dev/null 2>&1; then
  npm install -g pnpm
fi

if ! run_as_user "command -v rustup" >/dev/null 2>&1; then
  run_as_user "curl https://sh.rustup.rs -sSf | sh -s -- -y"
fi

if ! run_as_user "command -v pipx" >/dev/null 2>&1; then
  run_as_user "python3 -m pip install --user -U pipx && pipx ensurepath"
else
  run_as_user "pipx ensurepath"
fi

run_as_user "pipx install poetry --force"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_DIR=$(cd "${SCRIPT_DIR}/.." && pwd)

cd "${REPO_DIR}"

if [[ ! -f .env ]]; then
  cp .env.example .env
fi
if [[ -d bigdata && -f bigdata/.env.example && ! -f bigdata/.env ]]; then
  cp bigdata/.env.example bigdata/.env
fi

read -rp "Admin API key (e.g., demo-key): " ADMIN_KEY
ADMIN_KEY=${ADMIN_KEY:-demo-key}
read -rp "Gateway HTTP port [8080]: " GATEWAY_PORT
GATEWAY_PORT=${GATEWAY_PORT:-8080}
read -rp "Console URL (NEXTAUTH_URL) [http://localhost:3000]: " NEXTAUTH_URL
NEXTAUTH_URL=${NEXTAUTH_URL:-http://localhost:3000}
read -rp "Control gRPC endpoint [localhost:50051]: " CONTROL_GRPC
CONTROL_GRPC=${CONTROL_GRPC:-localhost:50051}

update_env() {
  local key="$1"
  local value="$2"
  local file="$3"
  python3 - "$file" "$key" "$value" <<'PY'
import sys
path, key, value = sys.argv[1:4]
with open(path, 'r', encoding='utf-8') as fh:
    lines = fh.read().splitlines()
found = False
for idx, line in enumerate(lines):
    if line.startswith(f"{key}="):
        lines[idx] = f"{key}={value}"
        found = True
        break
if not found:
    lines.append(f"{key}={value}")
with open(path, 'w', encoding='utf-8') as fh:
    fh.write("\n".join(lines) + "\n")
PY
}

update_env "AION_GATEWAY_API_KEYS" "${ADMIN_KEY}:admin" .env
update_env "AION_GATEWAY_PORT" "${GATEWAY_PORT}" .env
update_env "AION_CONTROL_GRPC" "${CONTROL_GRPC}" .env
update_env "NEXTAUTH_URL" "${NEXTAUTH_URL}" .env
update_env "NEXT_PUBLIC_GATEWAY_URL" "http://localhost:${GATEWAY_PORT}" .env

if command -v psql >/dev/null 2>&1; then
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='aion'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER aion WITH PASSWORD 'aion';"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='aiondb'" | grep -q 1 || \
    sudo -u postgres createdb -O aion aiondb
fi

run_as_user "cd \"${REPO_DIR}/control\" && poetry install && poetry run alembic upgrade head"
run_as_user "cd \"${REPO_DIR}/gateway\" && pnpm install && pnpm build"
run_as_user "cd \"${REPO_DIR}/modules\" && cargo build --release"
run_as_user "cd \"${REPO_DIR}/console\" && pnpm install && pnpm build"

cat <<INFO
[bootstrap-native] environment prepared.
- Control (FastAPI) env ready. Run: (cd control && poetry run uvicorn aion.control.app:app --host 0.0.0.0 --port 8000)
- Gateway ready. Run: (cd gateway && pnpm start)
- Console ready. Run: (cd console && pnpm start)
INFO
