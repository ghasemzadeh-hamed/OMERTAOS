# Secret management

AION-OS centralises credentials and sensitive configuration in HashiCorp Vault. Every
service reads secrets at runtime via the shared secret provider libraries so that
application code and configuration files never contain long-lived tokens, passwords or
keys.

## Environment contract

All services understand the following Vault configuration variables:

- `AION_VAULT_ADDR` - URL of the Vault API endpoint (for example
  `http://vault:8200`).
- `AION_VAULT_KV_MOUNT` - mount name of the KV-v2 engine that stores secrets
  (defaults to `secret`).
- `AION_VAULT_TOKEN` - development token when using token authentication.
- `AION_VAULT_AUTH_METHOD` - optional override of the authentication strategy
  (`token` for local development or `approle` in production).
- `AION_VAULT_APPROLE_ROLE_ID` / `AION_VAULT_APPROLE_SECRET_ID` - credentials for
  the AppRole associated with the service when `AION_VAULT_AUTH_METHOD=approle`.
- `AION_VAULT_NAMESPACE` - optional namespace when operating against HCP Vault or
  Vault Enterprise.
- `AION_ENV` - deployment environment label (`dev`, `staging`, `prod`, ...).

Each service consumes only Vault secret paths:

- `AION_DB_SECRET_PATH` - PostgreSQL (and future relational) credentials.
- `AION_MINIO_SECRET_PATH` - object storage endpoint and credentials.
- `AION_JWT_SECRET_PATH` - JWT public key bundle for the gateway.
- `AION_GATEWAY_API_KEYS_SECRET_PATH` - API key catalogue for gateway clients.
- `AION_ADMIN_TOKEN_SECRET_PATH` - privileged bearer token shared by gateway and console.

Secret payloads are stored in a KV-v2 engine and may be updated without restarting
services. For example, the database secret should contain:

```json
{
  "username": "aionos",
  "password": "...",
  "host": "postgres",
  "port": 5432,
  "database": "aionos"
}
```

## Local development

A helper script bootstraps a Vault dev cluster with integrated Raft storage, enables the
`secret/` KV engine, seeds development secrets and provisions a scoped token:

```bash
scripts/bootstrap_vault_dev.py
```

The script starts the `vault` service defined in `docker-compose.yml`, initialises and
unseals it (storing the unseal key under `.vault/dev-unseal.json`), generates a fresh
development certificate authority and service certificates, seeds Vault with those
artifacts and writes a reusable development token to `.env.vault.dev`. Source that file
alongside your regular `.env` before running the stack:

```bash
source .env
source .env.vault.dev
docker compose up -d
```

If Vault takes longer than the default three minutes to become reachable (for example,
when pulling the container image for the first time), set
`AION_VAULT_BOOTSTRAP_TIMEOUT=<seconds>` before running the script to extend the wait.

Replace the placeholder TLS certificates inside Vault with material generated from the
freshly-created development CA before exposing services.

> **Note**: The bootstrap script depends on the `hvac`, `cryptography` and `requests`
> Python packages. Install them via `pip install hvac cryptography requests` if they are
> not already available in your environment.

## Production and HCP Vault

For production deployments the same configuration applies. Provision a Vault cluster with
integrated storage (or HCP Vault) and create the policies from `policies/vault`. Bind each
service to an AppRole and distribute only the role ID and wrapped secret ID at deploy time.

- Rotate credentials by updating the KV entry; services automatically pick up the new
  values without redeploying.
- Use namespaced mounts when operating with HCP Vault by setting `AION_VAULT_NAMESPACE`.
- Restrict network access so only platform hosts can reach Vault.

## Updating backend services

To register or change backing databases or object stores update the relevant Vault
secret(s) only:

- Update `kv/data/aionos/db-main` with new connection details to move control-plane
  storage to another PostgreSQL instance.
- Update `kv/data/aionos/minio` when swapping MinIO for S3-compatible storage. The
  control service rebuilds its client on next access.
- Rotate gateway API keys or JWT material by writing new data to their respective secrets.

No configuration files or `.env` entries require editing-restart services only if the
underlying infrastructure changed (for example, hostname migrations).

## Secret provider libraries

- Python services use `os.secrets.SecretProvider` (backed by `hvac`) to read Vault
  secrets and construct connection strings at startup.
- Node.js services consume `@aionos/secret-provider`, a lightweight fetch-based client
  shared by the gateway and console.

Both implementations honour the environment contract above and support local dev tokens
and AppRole credentials without code changes.
