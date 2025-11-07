#!/usr/bin/env bash
set -euo pipefail

echo "AION-OS Interactive Installer (Native, no Docker)"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# ---- 0) Sanity & sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run via: sudo bash scripts/install.sh"
  exit 1
fi
SUDO_USER=${SUDO_USER:-root}

# ---- 1) Ask config
read -p "Admin username: " ADMIN_USER
read -s -p "Admin password: " ADMIN_PASS; echo
read -p "Domain or IP for UI (e.g., aionos.local or 127.0.0.1): " DOMAIN
read -p "UI (Console) port [3000]: " UI_PORT; UI_PORT=${UI_PORT:-3000}
read -p "Gateway port [8080]: " GATEWAY_PORT; GATEWAY_PORT=${GATEWAY_PORT:-8080}
read -p "Control HTTP port [8000]: " CONTROL_HTTP_PORT; CONTROL_HTTP_PORT=${CONTROL_HTTP_PORT:-8000}
read -p "Control gRPC endpoint host:port [127.0.0.1:50051]: " CONTROL_GRPC; CONTROL_GRPC=${CONTROL_GRPC:-127.0.0.1:50051}
read -p "Tenancy mode single/multi [single]: " TENANCY_MODE; TENANCY_MODE=${TENANCY_MODE:-single}
read -p "Create Postgres (user/db aionos) locally? y/N: " MAKE_PG; MAKE_PG=${MAKE_PG:-N}
read -p "Also install MongoDB? y/N: " MAKE_MONGO; MAKE_MONGO=${MAKE_MONGO:-N}

# initial gateway API key (admin)
read -p "Initial Gateway API key name [demo-key]: " API_KEY_NAME; API_KEY_NAME=${API_KEY_NAME:-demo-key}

# NEXTAUTH secret
NEXTAUTH_SECRET=$(tr -dc A-Za-z0-9 </dev/urandom | head -c 48)

echo
echo "Summary:"
echo "  DOMAIN=$DOMAIN"
echo "  UI_PORT=$UI_PORT, GATEWAY_PORT=$GATEWAY_PORT, CONTROL_HTTP_PORT=$CONTROL_HTTP_PORT, CONTROL_GRPC=$CONTROL_GRPC"
echo "  TENANCY_MODE=$TENANCY_MODE"
echo "  API KEY: $API_KEY_NAME -> roles: admin|manager"
read -p "Press Enter to proceed..."

# ---- 2) Packages
apt-get update
apt-get install -y curl build-essential python3 python3-venv python3-pip \
  redis-server postgresql postgresql-contrib ca-certificates gnupg

# ---- 3) Node via NVM (to ensure recent LTS)
if ! command -v node >/dev/null 2>&1; then
  su - "$SUDO_USER" -c 'curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash'
  su - "$SUDO_USER" -c 'export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh" && nvm install --lts && nvm alias default lts/*'
fi
# resolve node/npm path for root shells too
if [ -d "/root/.nvm" ]; then
  . /root/.nvm/nvm.sh || true
fi

# ---- 4) Optional DBs
if [[ "$MAKE_PG" =~ ^[Yy]$ ]]; then
  systemctl enable --now postgresql
  sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='aionos'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER aionos WITH PASSWORD 'aionos123';"
  sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='aionos'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE aionos OWNER aionos;"
fi

if [[ "$MAKE_MONGO" =~ ^[Yy]$ ]]; then
  # Quick community install (Ubuntu, may add official repo in production)
  apt-get install -y mongodb
  systemctl enable --now mongodb || true
fi

systemctl enable --now redis-server

# ---- 5) Create .env (root) before builds
POSTGRES_DSN="postgresql://aionos:aionos123@localhost:5432/aionos"
REDIS_URL="redis://localhost:6379/0"
GATEWAY_API_KEYS="${API_KEY_NAME}:admin|manager"

cat > "$REPO_DIR/.env" <<EOF_ENV
# === aionOS root env ===
ADMIN_USER=${ADMIN_USER}
ADMIN_PASS=${ADMIN_PASS}

# Gateway
AION_GATEWAY_PORT=${GATEWAY_PORT}
AION_CONTROL_GRPC=${CONTROL_GRPC}
AION_GATEWAY_API_KEYS=${GATEWAY_API_KEYS}
AION_RATE_LIMIT_MAX=60
AION_RATE_LIMIT_PER_IP=30
AION_TLS_CERT=
AION_TLS_KEY=

# Control (FastAPI)
AION_CONTROL_REDIS_URL=${REDIS_URL}
AION_CONTROL_POSTGRES_DSN=${POSTGRES_DSN}
AION_CONTROL_MONGO_DSN=
TENANCY_MODE=${TENANCY_MODE}

# Console (Next.js)
NEXTAUTH_URL=http://${DOMAIN}:${UI_PORT}
NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
NEXT_PUBLIC_GATEWAY_URL=http://${DOMAIN}:${GATEWAY_PORT}
NEXT_PUBLIC_CONTROL_URL=http://${DOMAIN}:${CONTROL_HTTP_PORT}
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
EOF_ENV

# ---- 6) Python Control setup
echo ">> Setting up Control (FastAPI)..."
cd "$REPO_DIR/control"
python3 -m venv .venv
. .venv/bin/activate
pip install -U pip wheel setuptools
# if requirements.txt exists, install; otherwise best-effort
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
# auto-detect FastAPI app module (find 'FastAPI(' and 'app = FastAPI')
APP_MODULE=$(grep -RIl "FastAPI\(" . | head -n1 | sed 's|^./||')
# convert path to module: replace / with . and strip .py
if [[ -n "$APP_MODULE" ]]; then
  MOD="${APP_MODULE%.*}"
  MOD="${MOD//\//.}"
  UVICORN_APP="${MOD}:app"
else
  # fallback commonly used path per README (app.control.main:app)
  UVICORN_APP="app.control.main:app"
fi
echo "$UVICORN_APP" > .uvicorn_app
deactivate

# ---- 7) Gateway (Node)
echo ">> Setting up Gateway (Node)..."
cd "$REPO_DIR/gateway"
if [ -f package-lock.json ] || [ -f package.json ]; then
  su - "$SUDO_USER" -c "cd '$REPO_DIR/gateway' && . \\$HOME/.nvm/nvm.sh && npm ci || npm install"
  su - "$SUDO_USER" -c "cd '$REPO_DIR/gateway' && . \\$HOME/.nvm/nvm.sh && npm run build || true"
fi

# ---- 8) Console (Next.js)
echo ">> Building Console (Next.js)..."
cd "$REPO_DIR/console" 2>/dev/null || cd "$REPO_DIR/web" 2>/dev/null || mkdir -p "$REPO_DIR/console" && cd "$REPO_DIR/console"
if [ -f package.json ]; then
  su - "$SUDO_USER" -c "cd '$PWD' && . \\$HOME/.nvm/nvm.sh && npm ci || npm install"
  su - "$SUDO_USER" -c "cd '$PWD' && . \\$HOME/.nvm/nvm.sh && npm run build || npx next build"
fi

# ---- 9) systemd services
echo ">> Creating systemd services..."
cat > /etc/systemd/system/aionos-control.service <<SERVICE
[Unit]
Description=AIONOS Control (FastAPI)
After=network.target
[Service]
User=${SUDO_USER}
WorkingDirectory=${REPO_DIR}/control
EnvironmentFile=${REPO_DIR}/.env
Environment="PATH=${REPO_DIR}/control/.venv/bin"
ExecStart=${REPO_DIR}/control/.venv/bin/uvicorn \$(cat ${REPO_DIR}/control/.uvicorn_app) --host 0.0.0.0 --port ${CONTROL_HTTP_PORT}
Restart=on-failure
[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/aionos-gateway.service <<SERVICE
[Unit]
Description=AIONOS Gateway (Node.js)
After=network.target aionos-control.service
[Service]
User=${SUDO_USER}
WorkingDirectory=${REPO_DIR}/gateway
EnvironmentFile=${REPO_DIR}/.env
ExecStart=/bin/bash -lc '. \\$HOME/.nvm/nvm.sh && npm start --silent || node dist/index.js'
Restart=on-failure
[Install]
WantedBy=multi-user.target
SERVICE

cat > /etc/systemd/system/aionos-console.service <<SERVICE
[Unit]
Description=AIONOS Console (Next.js)
After=network.target
[Service]
User=${SUDO_USER}
WorkingDirectory=${REPO_DIR}/console
EnvironmentFile=${REPO_DIR}/.env
ExecStart=/bin/bash -lc '. \\$HOME/.nvm/nvm.sh && npx --yes next start -p ${UI_PORT}'
Restart=on-failure
[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable aionos-control aionos-gateway aionos-console
systemctl restart aionos-control aionos-gateway aionos-console

echo "Done."
echo "Gateway: http://${DOMAIN}:${GATEWAY_PORT}   (set via AION_GATEWAY_PORT)"
echo "Control: http://${DOMAIN}:${CONTROL_HTTP_PORT}/healthz"
echo "Console: http://${DOMAIN}:${UI_PORT}"
