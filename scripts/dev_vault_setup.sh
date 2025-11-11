#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

VAULT_ADDR=http://127.0.0.1:8200
VAULT_DEV_ROOT_TOKEN_ID=root
ENV_FILE=".env.vault.dev"

echo "[vault-dev] Starting local Vault dev server..."

if ! command -v vault >/dev/null 2>&1; then
  echo "[vault-dev] ERROR: 'vault' CLI not found in PATH."
  echo "[vault-dev] Install from https://developer.hashicorp.com/vault/downloads"
  exit 1
fi

# Start dev server in background
vault server \
  -dev \
  -dev-root-token-id="${VAULT_DEV_ROOT_TOKEN_ID}" \
  -config="${ROOT_DIR}/config/vault-dev.hcl" \
  > .vault-dev.log 2>&1 &

VAULT_PID=$!

# Wait for Vault to be ready
echo -n "[vault-dev] Waiting for Vault to be ready"
for i in {1..30}; do
  if curl -s "${VAULT_ADDR}/v1/sys/health" >/dev/null 2>&1; then
    echo " -> OK"
    break
  fi
  echo -n "."
  sleep 1
done

if ! curl -s "${VAULT_ADDR}/v1/sys/health" >/dev/null 2>&1; then
  echo
  echo "[vault-dev] ERROR: Vault did not become ready. Check .vault-dev.log"
  kill "${VAULT_PID}" || true
  exit 1
fi

export VAULT_ADDR
export VAULT_TOKEN="${VAULT_DEV_ROOT_TOKEN_ID}"

echo "[vault-dev] Login with root token..."
vault login -no-print "${VAULT_DEV_ROOT_TOKEN_ID}" >/dev/null

# Enable KV v2 if not exists
if ! vault secrets list -format=json | grep -q '"secret/":'; then
  echo "[vault-dev] Enabling KV secrets engine at 'secret/'..."
  vault secrets enable -path=secret kv-v2 >/dev/null
fi

# Example test secrets (اختیاری؛ برای ستاپ اولیه)
echo "[vault-dev] Writing sample dev secrets..."
vault kv put secret/aionos/dev-db \
  username="aionos_dev" \
  password="dev-password" \
  >/dev/null

vault kv put secret/aionos/dev-api \
  api_key="dev-api-key" \
  >/dev/null

# Generate .env.vault.dev
cat > "${ENV_FILE}" <<EOF2
VAULT_ADDR=${VAULT_ADDR}
VAULT_TOKEN=${VAULT_DEV_ROOT_TOKEN_ID}
VAULT_KV_MOUNT=secret
AION_VAULT_ENABLED=true
EOF2

echo "[vault-dev] Wrote ${ENV_FILE}:"
cat "${ENV_FILE}"

echo
echo "[vault-dev] Dev Vault is running (PID=${VAULT_PID})."
echo "[vault-dev] Use this file in CI: \`cat .env.vault.dev >> \$GITHUB_ENV\`"
