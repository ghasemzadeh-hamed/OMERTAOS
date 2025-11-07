# Runbook

## Bootstrapping

1. Provision infrastructure (Kubernetes cluster with GPU and CPU pools).
2. Deploy data services (PostgreSQL, Redis, MongoDB, Kafka, Qdrant, MinIO).
3. Deploy control plane and gateway manifests under `deploy/k8s/`.
4. Configure TLS certificates and upload Cosign public keys.

## Health Checks

- Gateway: `GET /healthz`
- Control: `GET /healthz`
- Modules: `/healthz` endpoints exposed by hosts
- Kafka: Ensure topics exist via `kafka-topics.sh --list`

## Incident Response

| Scenario | Action |
|----------|--------|
| Gateway returns 429 | Increase rate limit or investigate abuse; verify Redis availability |
| Task latency spike | Review `aion.metrics.runtime` topic, inspect Grafana Router dashboard |
| Policy regression | Re-run Airflow `weekly_model_train` DAG and call `/v1/router/policy/reload` |
| Module failure | Check module host logs, verify Cosign signatures, roll back manifest |

## Approvals & Guardrails

- Admin approvals: changes to kernel or networking are proposed through the Console and require an approver with the `kernel.admin` role. The API endpoint `/v1/kernel/proposals/{id}/approve` validates RBAC and emits an audit record to Kafka (`kernel.proposals`).
- Webhook approvals: signed inbound webhooks hitting `/v1/hooks/approval` must include an HMAC signature header. Verification keys live in Vault (`secret/omertaos/hooks`). Failed verification must be treated as a security incident.
- Rollback workflow: invoke `/v1/kernel/proposals/{id}/rollback` or use the Console rollback button. Confirm rollback completion via Grafana "Kernel" dashboard (panel `k_rollbacks_total`).
- Cosign enforcement: production module containers must have signatures verified during deploy by the GitHub Action `verify-cosign`. Missing signatures are a hard failure; consult `deploy/cosign/README.md`.

## Backups

- PostgreSQL: nightly pg_dump to MinIO bucket `aion-backups/pg`
- MongoDB: use `mongodump` to MinIO
- ClickHouse: replicate to S3-compatible storage using `S3` table engine

## Key Rotation

1. Generate new API key via secure secret store.
2. Update `AION_GATEWAY_API_KEYS` secret and reload gateway Deployment.
3. Rotate JWT signing keys; publish new public key to gateway config.
4. Update Cosign key pair; re-sign images and update `modules.yml` checksums.

## Rollback

- Control policies: restore previous YAML from Git and call reload endpoint.
- Modules: revert to previous manifest version and reapply via ORAS registry.
- Data pipelines: redeploy last stable Airflow DAG tag.

## Webhook Operations

- Outbound: webhooks are retried with exponential backoff up to 5 times. Failed deliveries surface in Grafana (panel `webhook_failures_total`). Payloads include `x-omerta-signature` for downstream verification.
- Inbound: verify required headers (`x-omerta-signature`, `Tenant-ID`) and enforce RBAC scopes. Redis-backed idempotency keys live in `redis://redis:6379/3` and expire after 24h. Legacy `x-tenant-id` and `x-tenant` headers are accepted for older agents.

## Memory Operations

- Ingestion: use `POST /v1/memory/ingest` with base64 encoded chunks. Resume uploads by repeating the request with the same `upload_id` and `chunk_index`.
- Profiles: configure ingestion behavior with `POST /v1/memory/profile` (fields: `name`, `embedding_model`, `chunk_size`, `pipeline`, `retention_days`).
- Status: retrieve active uploads and profile catalog via `GET /v1/memory/status`. Completed uploads expose `checksum` and byte counts for audit.
- Lifecycle: MinIO bucket policies are defined in `deploy/minio/lifecycle.json`; confirm retention with `mc ilm ls minio/memory`.

## Redis & Kafka Recovery

- Redis: fail-closed behaviour means rate-limited routes will reject requests when Redis is unavailable. Restore by restarting `redis` deployment and replaying any buffered kernel proposals.
- Kafka: monitor topic lags via `kafka-consumer-groups.sh --bootstrap-server kafka:9092 --group control-plane --describe`. Recreate missing topics with manifests in `deploy/kafka/topics/`.

## MinIO Lifecycle

- Lifecycle policies use the `memory-retention` rule. To adjust, update `deploy/minio/lifecycle.json` and reapply with `mc ilm import`.
- Multipart uploads older than 72 hours are automatically aborted. Verify clean-up jobs in Grafana "Object Storage" dashboard.

## ClickHouse TTL

- TTL scripts reside in `bigdata/sql/clickhouse_retention.sql`. Apply with `clickhouse-client -n < bigdata/sql/clickhouse_retention.sql`.
- Confirm TTL effectiveness by checking `system.parts` for expired partitions.

## Secret Rotation

- Secrets are stored in Vault via SOPS. Update encrypted files under `policies/secrets/` and re-encrypt with `sops -e`.
- Synchronise secrets to Kubernetes using `scripts/sync_secrets.sh`. Verify Cosign keys post-rotation.

## Scaling

- Gateway HPA monitors CPU and request latency.
- Control plane scales based on p95 latency and queue depth metrics.
- Module hosts separate GPU/CPU pools declared through node selectors.

## Retention

- Mongo TTL indexes created by `os/control/os/db/retention_mongo.py` enforce 7-14 day (dev) or 30-90 day (prod) log expiry.
- ClickHouse TTL scripts under `bigdata/sql/clickhouse_retention.sql` can be applied via `clickhouse-client -f`.
- Override retention by exporting `AION_LOG_TTL_DAYS` and `AION_CLICKHOUSE_TTL_DAYS`.
