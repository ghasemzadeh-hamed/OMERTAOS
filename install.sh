#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# AION-OS – Linux/WSL one-shot installer (AIONOS branch)
# This script can be executed either before cloning the repo
# (it will clone into ./OMERTAOS) or from inside an existing
# checkout (it will reuse the current directory).
# ------------------------------------------------------------

echo -e "\U0001F680 AION-OS – Linux/WSL Installer (AIONOS branch)\n"

need() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ $1 not found. Please install and retry." >&2
    exit 1
  fi
}

need git
need docker
need awk
need sed
need uuidgen

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
if [ -d "$SCRIPT_DIR/.git" ]; then
  TARGET_DIR="$SCRIPT_DIR"
  cd "$TARGET_DIR"
  echo "ℹ️  Existing OMERTAOS repository detected at $TARGET_DIR"
  DEFAULT_REPO_URL=$(git remote get-url origin 2>/dev/null || echo "https://github.com/ghasemzadeh-hamed/OMERTAOS.git")
else
  TARGET_DIR="$(pwd)/OMERTAOS"
  DEFAULT_REPO_URL="https://github.com/ghasemzadeh-hamed/OMERTAOS.git"
fi

read -r -p "🔗 Repo URL [$DEFAULT_REPO_URL]: " REPO
REPO=${REPO:-$DEFAULT_REPO_URL}
read -r -p "🌿 Branch [AIONOS]: " BRANCH
BRANCH=${BRANCH:-AIONOS}

read -r -p "👤 Admin user [admin]: " ADMIN_USER
ADMIN_USER=${ADMIN_USER:-admin}
read -r -p "🔑 Admin pass (min 8 chars) [admin1234]: " ADMIN_PASS
ADMIN_PASS=${ADMIN_PASS:-admin1234}

read -r -p "🖥️  UI port (console) [3000]: " UI_PORT
UI_PORT=${UI_PORT:-3000}
read -r -p "🌐 Gateway port [8080]: " GW_PORT
GW_PORT=${GW_PORT:-8080}
read -r -p "⚙️  FastAPI port [8000]: " API_PORT
API_PORT=${API_PORT:-8000}

read -r -p "🗄️  Postgres user [postgres]: " PG_USER
PG_USER=${PG_USER:-postgres}
read -r -p "🔐 Postgres pass [postgres]: " PG_PASS
PG_PASS=${PG_PASS:-postgres}
read -r -p "📚 Postgres DB [aionos]: " PG_DB
PG_DB=${PG_DB:-aionos}

read -r -p "🧠 Redis URL [redis://redis:6379]: " REDIS_URL
REDIS_URL=${REDIS_URL:-redis://redis:6379}
read -r -p "🗂️  MinIO Console URL [http://localhost:9001]: " MINIO_URL
MINIO_URL=${MINIO_URL:-http://localhost:9001}

read -r -p "📊 Enable BigData overlay? (y/N): " USE_BIGDATA
USE_BIGDATA=${USE_BIGDATA:-N}

if [ "$TARGET_DIR" != "$SCRIPT_DIR" ]; then
  if [ -d "$TARGET_DIR/.git" ]; then
    echo "ℹ️  OMERTAOS exists at $TARGET_DIR; pulling latest…"
    cd "$TARGET_DIR"
    git fetch origin "$BRANCH"
    git checkout "$BRANCH"
    git pull origin "$BRANCH"
  else
    git clone -b "$BRANCH" --single-branch "$REPO" "$TARGET_DIR"
    cd "$TARGET_DIR"
  fi
else
  git fetch origin "$BRANCH" 2>/dev/null || true
  git checkout "$BRANCH"
  git pull origin "$BRANCH" 2>/dev/null || true
fi

write_env() {
  local path="$1"
  local data="$2"
  mkdir -p "$(dirname "$path")"
  printf "%s" "$data" > "$path"
  echo "✅ wrote $path"
}

FASTAPI_URL="http://control:$API_PORT"
GATEWAY_URL="http://gateway:$GW_PORT"
NEXTAUTH_SECRET=$(uuidgen | tr -d '-')

write_env "console/.env" "$(cat <<EOF
NEXT_PUBLIC_API_BASE=$GATEWAY_URL
NEXTAUTH_SECRET=$NEXTAUTH_SECRET
NEXTAUTH_URL=http://localhost:$UI_PORT
DATABASE_URL=postgresql://$PG_USER:$PG_PASS@postgres:5432/$PG_DB
REDIS_URL=$REDIS_URL
ADMIN_SEED_USER=$ADMIN_USER
ADMIN_SEED_PASS=$ADMIN_PASS
FASTAPI_URL=$FASTAPI_URL
EOF
)"

write_env "gateway/.env" "$(cat <<EOF
PORT=$GW_PORT
CONTROL_BASE_URL=$FASTAPI_URL
REDIS_URL=$REDIS_URL
ALLOW_ORIGIN=*
EOF
)"

write_env "control/.env" "$(cat <<EOF
PORT=$API_PORT
POSTGRES_DSN=postgresql://$PG_USER:$PG_PASS@postgres:5432/$PG_DB
REDIS_URL=$REDIS_URL
MINIO_ENDPOINT=http://minio:9000
EOF
)"

if [[ "$USE_BIGDATA" =~ ^[Yy]$ ]]; then
  if [ -f "docker-compose.bigdata.yml" ]; then
    echo "🟣 Starting with BigData overlay…"
    docker compose -f docker-compose.yml -f docker-compose.bigdata.yml up -d --build
  elif [ -f "bigdata/docker-compose.bigdata.yml" ]; then
    echo "🟣 Starting with BigData overlay (bigdata/docker-compose.bigdata.yml)…"
    docker compose -f docker-compose.yml -f bigdata/docker-compose.bigdata.yml up -d --build
  else
    echo "⚠️  BigData overlay file not found. Starting core stack."
    docker compose up -d --build
  fi
else
  echo "🟢 Starting core stack…"
  docker compose up -d --build
fi

sleep 5
echo -e "\n📡 Containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n🌐 URLs:"
echo "UI (console):     http://localhost:$UI_PORT"
echo "Gateway:          http://localhost:$GW_PORT"
echo "FastAPI (docs):   http://localhost:$API_PORT/docs"
echo "MinIO Console:    $MINIO_URL (if BigData enabled)"

echo -e "\n✅ Done. First boot may take a few seconds for DB migrations/seed."
