# Operational Runbook

## 1. Bootstrapping
1. Deploy via Docker Compose (`docker compose up`) for development or use Kubernetes with HPA for production.
2. Verify gateway and control plane health endpoints (`/healthz`).
3. Apply service mesh policies and ensure mTLS between services.

## 2. Secrets & Keys
1. Populate Vault/SOPS with provider API keys and internal secrets.
2. Configure control plane access to secrets through hostcalls only.
3. Enforce cosign signature verification before module installation.

## 3. Policy Management
1. Validate `intents.yml`, `policies.yml`, `models.yml`, and `modules.yml` using `aionctl validate`.
2. Apply policies via control plane API and confirm audit events in Kafka (`aion.audit.activity`).
3. Trigger policy reload using `POST /router/policy/reload` and verify version tags.

## 4. Observability
1. Ensure OTEL collector is receiving traces from gateway, control plane, and modules.
2. Verify Prometheus targets and Grafana dashboards:
   - Router Overview (route distribution, cost/task, latency percentiles)
   - Task Health (throughput, retries, failure heatmap)
   - Resource Utilization (CPU/RAM/GPU, Kafka lag)
3. Confirm log retention policies: Mongo TTL 7–14 days (dev) / 30–90 days (prod); ClickHouse TTL 90 days.

## 5. Kafka Operations
1. Create required topics (`aion.router.decisions`, `aion.tasks.lifecycle`, `aion.metrics.runtime`, `aion.audit.activity`).
2. Apply ACLs using SASL/SCRAM or mTLS identities per service.
3. Monitor consumer lag and partition health via Grafana.

## 6. Module Lifecycle
1. Install new modules via `aionctl install ghcr.io/<module>:<version>`.
2. Validate WASM runtime compatibility or configure subprocess sandboxes.
3. Conduct smoke tests for each intent path (local/api/hybrid) and confirm metrics emission.

## 7. Incident Response
1. Identify failing tier/provider using Grafana and Kafka audit logs.
2. Apply circuit breakers or adjust routing fallback order.
3. Switch intents to `local-only` mode when privacy or outage concerns arise.
4. Reduce module parallelism if backpressure builds; notify stakeholders.

## 8. Release Management
1. Version configs and manifests; promote via GitOps pipelines.
2. Utilize canary deployments for gateway/control plane upgrades.
3. Maintain rollback scripts for policy versions and module artifacts.

## 9. Compliance & Security Checks
1. Run Grype/Trivy scans on module packages pre-release.
2. Verify SBOM presence and cosign signature validity.
3. Audit API key usage and enforce rotation schedules.

## 10. Disaster Recovery
1. Backup Postgres, Mongo, and MinIO using scheduled snapshots.
2. Replicate Kafka topics cross-region when residency policy allows.
3. Document RTO/RPO targets aligned with SLOs (default RTO 1h, RPO 15m).
