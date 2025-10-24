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

## Scaling

- Gateway HPA monitors CPU and request latency.
- Control plane scales based on p95 latency and queue depth metrics.
- Module hosts separate GPU/CPU pools declared through node selectors.

## Retention

- Mongo TTL indexes created by `control/app/db/retention_mongo.py` enforce 7-14 day (dev) or 30-90 day (prod) log expiry.
- ClickHouse TTL scripts under `bigdata/sql/clickhouse_retention.sql` can be applied via `clickhouse-client -f`.
- Override retention by exporting `AION_LOG_TTL_DAYS` and `AION_CLICKHOUSE_TTL_DAYS`.
