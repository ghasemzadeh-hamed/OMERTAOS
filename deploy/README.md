# Deployment

**Document role:** deployment asset index. These assets are research and
evaluation inputs; their presence does not establish a successful installation
or production acceptance.

`deploy/` is the source of truth for Native, Docker, Kubernetes, observability,
bundle and CI deployment assets. Root and legacy copies were retired in S5;
new deployment changes belong only here.

OMERTAOS provides two primary Compose modes. `deploy/docker/compose/quickstart.yml`
is a self-contained evaluation topology. `deploy/docker/compose/full.yml` is the
configurable local/integration topology. Neither is a production security
baseline without secret, TLS, image and network hardening.

```bash
# Evaluation
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up --build -d

# Local/integration
cp .env.example .env
docker compose --project-directory . -f deploy/docker/compose/full.yml up --build -d
```

Kubernetes assets under `deploy/kubernetes/` define workloads, stateful dependencies, ingress, network policy and observability. Production should use an external secret manager, managed stateful services where appropriate, immutable digest-pinned images, non-root/read-only containers, resource requests/limits, pod disruption budgets, topology spread, autoscaling, mTLS, restrictive egress, backups and tested restore.

## Scripts

| Script | Purpose |
|---|---|
| `install.sh` | Full installation/profile setup from repository root |
| `deploy/native/scripts/install.sh` | Native-first installation wrapper |
| `deploy/docker/scripts/install.sh` | Minimal Docker quickstart bootstrap |
| `deploy/docker/scripts/restore.sh` | Restore a validated backup into a compatible deployment |

Inspect flags with `--help`, run from a clean checkout, and back up before install/restore operations. Restore requires a maintenance window or documented online procedure, checksum verification, matching schema versions, and post-restore health/reconciliation checks.

## Current CI scope

The current GitHub Actions workflow defines architecture tests, Python lint,
Rust Clippy/tests, a conditional integration-test directory, Bandit, Cargo
Audit, Trivy filesystem scanning, multi-architecture image builds, and SPDX SBOM
generation. Review the workflow result for the exact commit; configured jobs
are not evidence that a run passed.

Artifact signing, immutable environment promotion, production deployment,
database migration, and production rollback are not performed by the current CI
workflow and must not be inferred from the deployment design.

## Environment strategy

Non-secret defaults live in versioned examples and deployment overlays. Secrets are external references injected at runtime. Variables are namespaced by service, validated on startup, and documented in service READMEs. Development permits local credentials and exposed diagnostics; production requires HA, TLS/mTLS, restricted ports, durable backups/retention, audited admin operations, SLO alerts, capacity limits, and disabled debug/dev authentication.
