# Deployment

OMERTAOS provides two Compose modes. `docker-compose.quickstart.yml` is a self-contained evaluation topology with development defaults and host ports for Console, Gateway and Control. `docker-compose.yml` is the configurable local/integration topology with health checks, optional Vault/observability profiles, persistent volumes, and stricter service configuration. Neither file is a production security baseline without secret, TLS, image and network hardening.

```bash
# Evaluation
docker compose -f docker-compose.quickstart.yml up --build -d

# Local/integration
cp .env.example .env
docker compose -f docker-compose.yml up --build -d
```

Kubernetes assets under `deploy/k8s/` define workloads, stateful dependencies, ingress, network policy and observability. Production should use an external secret manager, managed stateful services where appropriate, immutable digest-pinned images, non-root/read-only containers, resource requests/limits, pod disruption budgets, topology spread, autoscaling, mTLS, restrictive egress, backups and tested restore.

## Scripts

| Script | Purpose |
|---|---|
| `install.sh` | Full installation/profile setup from repository root |
| `quick-install.sh` | Minimal supported quickstart bootstrap |
| `deploy/scripts/restore.sh` | Restore a validated backup into a compatible deployment |

Inspect flags with `--help`, run from a clean checkout, and back up before install/restore operations. Restore requires a maintenance window or documented online procedure, checksum verification, matching schema versions, and post-restore health/reconciliation checks.

## CI/CD

The pipeline lints and unit-tests each service, validates schemas and architecture boundaries, builds generated clients, runs integration/security tests, builds SBOM-producing images, scans dependencies/images/secrets, signs artifacts, and publishes immutable digests. Deployment promotes the same digest through development, staging and production, applies expand migrations, runs readiness/smoke tests, and supports rollback or forward-fix. Production promotion requires approvals and preserves audit evidence.

## Environment strategy

Non-secret defaults live in versioned examples and deployment overlays. Secrets are external references injected at runtime. Variables are namespaced by service, validated on startup, and documented in service READMEs. Development permits local credentials and exposed diagnostics; production requires HA, TLS/mTLS, restricted ports, durable backups/retention, audited admin operations, SLO alerts, capacity limits, and disabled debug/dev authentication.
