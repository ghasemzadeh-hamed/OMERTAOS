#!/usr/bin/env bash
set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-https://127.0.0.1:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-root}"
VAULT_NAMESPACE="${VAULT_NAMESPACE:-}"
SECRETS_MOUNT="${SECRETS_MOUNT:-kv}"
POLICY_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/policies/vault"

export VAULT_ADDR
export VAULT_TOKEN
export VAULT_NAMESPACE

command -v vault >/dev/null 2>&1 || {
  echo "[setup_vault_local] Vault CLI is required" >&2
  exit 1
}
command -v jq >/dev/null 2>&1 || {
  echo "[setup_vault_local] jq is required" >&2
  exit 1
}

echo "[setup_vault_local] Using Vault at ${VAULT_ADDR}" >&2

vault status >/dev/null

if ! vault secrets list -format=json | jq -e ".\"${SECRETS_MOUNT}/\"" >/dev/null; then
  echo "[setup_vault_local] Enabling KV v2 secrets engine at mount '${SECRETS_MOUNT}'" >&2
  vault secrets enable -path="${SECRETS_MOUNT}" kv-v2
fi

echo "[setup_vault_local] Writing sample secrets" >&2
vault kv put "${SECRETS_MOUNT}/aionos/db-main" \
  username="aionos" \
  password="aionos-dev" \
  host="postgres" \
  port="5432" \
  database="aionos"

vault kv put "${SECRETS_MOUNT}/aionos/minio" \
  endpoint="minio:9000" \
  access_key="minio" \
  secret_key="miniosecret" \
  bucket="aion-raw" \
  secure=false

vault kv put "${SECRETS_MOUNT}/aionos/jwt" public_key="-----BEGIN PUBLIC KEY-----\nREPLACE_ME\n-----END PUBLIC KEY-----"

vault kv put "${SECRETS_MOUNT}/aionos/gateway-api-keys" \
  value="demo-key:admin|manager"

vault kv put "${SECRETS_MOUNT}/aionos/admin-token" token="change-me"

echo "[setup_vault_local] Installing policies" >&2
for policy in control gateway console kernel; do
  vault policy write "aion-${policy}" "${POLICY_DIR}/${policy}.hcl"
done

if ! vault auth list -format=json | jq -e '."approle/"' >/dev/null; then
  echo "[setup_vault_local] Enabling AppRole auth method" >&2
  vault auth enable approle
fi

output_dir="${OUTPUT_DIR:-./.vault}";
mkdir -p "${output_dir}"

create_approle() {
  local role_name="$1"
  local policy_name="$2"
  vault write "auth/approle/role/${role_name}" \
    token_policies="${policy_name}" \
    token_ttl="24h" \
    token_max_ttl="72h"

  local role_id secret_id
  role_id=$(vault read -field=role_id "auth/approle/role/${role_name}/role-id")
  secret_id=$(vault write -f -field=secret_id "auth/approle/role/${role_name}/secret-id")

  cat >"${output_dir}/${role_name}.env" <<ENV
VAULT_ADDR=${VAULT_ADDR}
VAULT_AUTH_METHOD=approle
VAULT_APPROLE_ROLE_ID=${role_id}
VAULT_APPROLE_SECRET_ID=${secret_id}
ENV
  echo "[setup_vault_local] AppRole credentials for ${role_name} written to ${output_dir}/${role_name}.env" >&2
}

create_approle "aion-control" "aion-control"
create_approle "aion-gateway" "aion-gateway"
create_approle "aion-console" "aion-console"
create_approle "aion-kernel" "aion-kernel"

echo "[setup_vault_local] Setup complete" >&2
