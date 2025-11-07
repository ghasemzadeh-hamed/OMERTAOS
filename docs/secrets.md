# Secret management

AION-OS centralises credentials and sensitive configuration in HashiCorp Vault. Every
service reads secrets at runtime via the shared secret provider libraries so that
application code and configuration files never contain long-lived tokens, passwords or
keys.

## Environment contract

All services understand the following Vault configuration variables:

- `VAULT_ADDR` – URL of the Vault API endpoint (for example `https://127.0.0.1:8200`).
- `VAULT_AUTH_METHOD` – authentication strategy (`token` for local development or
  `approle` in production).
- `VAULT_NAMESPACE` – optional namespace when using HCP Vault or Enterprise Vault.
- `VAULT_TOKEN` – development token when using `VAULT_AUTH_METHOD=token`.
- `VAULT_APPROLE_ROLE_ID` / `VAULT_APPROLE_SECRET_ID` – credentials for the
  AppRole associated with the service when `VAULT_AUTH_METHOD=approle`.

Each service consumes only Vault secret paths:

- `AION_DB_SECRET_PATH` – PostgreSQL (and future relational) credentials.
- `AION_MINIO_SECRET_PATH` – object storage endpoint and credentials.
- `AION_JWT_SECRET_PATH` – JWT public key bundle for the gateway.
- `AION_GATEWAY_API_KEYS_SECRET_PATH` – API key catalogue for gateway clients.
- `AION_ADMIN_TOKEN_SECRET_PATH` – privileged bearer token shared by gateway and console.

Secret payloads are stored in a KV-v2 engine and may be updated without restarting
services. For example, the database secret should contain:

```json
{
  "username": "aionos",
  "password": "…",
  "host": "postgres",
  "port": 5432,
  "database": "aionos"
}
```

## Local development

A helper script bootstraps a TLS-enabled Vault dev cluster with integrated Raft storage
and creates read-only policies for each service:

```bash
scripts/setup_vault_local.sh
```

The script expects the Vault CLI and `jq`. It performs the following:

1. Enables a KV-v2 engine mounted at `kv/` (configurable via `SECRETS_MOUNT`).
2. Seeds sample secrets for the database, MinIO, JWT, API keys and admin token.
3. Installs least-privilege policies from `policies/vault/*.hcl`.
4. Enables the AppRole auth method and generates role credentials for control, gateway,
   console and kernel services, writing them to `./.vault/<service>.env` for convenience.

Use the emitted `.env` snippet when launching services locally, for example:

```bash
export VAULT_ADDR=https://127.0.0.1:8200
export VAULT_AUTH_METHOD=approle
source ./.vault/aion-control.env
```

## Production and HCP Vault

For production deployments the same configuration applies. Provision a Vault cluster with
integrated storage (or HCP Vault) and create the policies from `policies/vault`. Bind each
service to an AppRole and distribute only the role ID and wrapped secret ID at deploy time.

- Rotate credentials by updating the KV entry; services automatically pick up the new
  values without redeploying.
- Use namespaced mounts when operating with HCP Vault by setting `VAULT_NAMESPACE`.
- Restrict network access so only platform hosts can reach Vault.

## Updating backend services

To register or change backing databases or object stores update the relevant Vault
secret(s) only:

- Update `kv/data/aionos/db-main` with new connection details to move control-plane
  storage to another PostgreSQL instance.
- Update `kv/data/aionos/minio` when swapping MinIO for S3-compatible storage. The
  control service rebuilds its client on next access.
- Rotate gateway API keys or JWT material by writing new data to their respective secrets.

No configuration files or `.env` entries require editing—restart services only if the
underlying infrastructure changed (for example, hostname migrations).

## Secret provider libraries

- Python services use `os.secrets.SecretProvider` (backed by `hvac`) to read Vault
  secrets and construct connection strings at startup.
- Node.js services consume `@aionos/secret-provider`, a lightweight fetch-based client
  shared by the gateway and console.

Both implementations honour the environment contract above and support local dev tokens
and AppRole credentials without code changes.
