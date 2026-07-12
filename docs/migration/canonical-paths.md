# Canonical paths contract

Status: frozen for Structure migration

Date: 2026-07-12

This document is the executable handoff from S0 inventory to S2-S5 migration.
It defines ownership; it does not authorize deletion or combine migration phases.

## Service chain

| Concern | Canonical source | Allowed caller / dependency | Forbidden bypass |
|---|---|---|---|
| Product UI | `console/` | Gateway public API only | Control, Runtime and data-store endpoints |
| API boundary | `gateway/` | Control versioned client; ephemeral Redis admission state | Domain database, ORM or `data/` implementation imports |
| Decisions | `control/` | Runtime client plus Data/Registry/Policy interfaces | Direct subprocess, shell, sandbox or host effects |
| Execution | `runtime-daemon/` | Versioned schemas and narrow shared primitives | Business planning, model selection or Control-table writes |

## Path mapping

| Legacy input | Canonical owner | Operation | Phase / retirement evidence |
|---|---|---|---|
| `control-plane/` | `control/` | `MERGE` | S2 imports, Control tests and service build pass |
| `orchestration/` | `control/orchestration/` | `MOVE` | S2 callers and scheduling tests pass |
| `rust-runtime/` | `runtime-daemon/` | `MERGE` | S2 Cargo build/test and gRPC contract pass |
| Runtime code in `execution/` | `runtime-daemon/` | `SPLIT` | S2 unique code and callers accounted for |
| `database/`, `db/` | `data/` | `MERGE` | S3 imports and adapter/transaction tests pass |
| Model metadata in `models/` | `registry/models/` | `MERGE` | S3 registry lookup/version tests pass |
| Model clients/providers in `models/` | `control/clients/models/`, `integrations/providers/` | `SPLIT` | S3 routing/provider contracts pass |
| `agents/` | Registry, Control, SDK, integrations or Runtime bundle | `SPLIT` | S3 every file classified by behavior |
| `protos`, `schemas/proto*`, private service protos | `schemas/v1/protos/` | `MERGE` | S3 generation and cross-language contract tests pass |
| Generated protobuf/client copies | `shared/generated/{python,typescript,rust}/` | `GENERATED` | Reproducible generation and clean diff pass |
| `eventbus/` | `schemas/v1/events/`, `control/ports/`, `integrations/eventbus/` | `SPLIT` | S3 event contract and adapter tests pass |
| `observability/` | `shared/telemetry/`, `integrations/observability/`, `deploy/observability/` | `SPLIT` | S3/S4 telemetry and deployment checks pass |
| `execution/windows-agentic-bridge/` | `integrations/windows-agentic-bridge/` | `MERGE` | S3 full diff and bridge builds/tests pass |
| `docker/`, `infra/`, deployment content in `execution/` | `deploy/` | `MERGE` | S4 Native and Quickstart configuration/smoke pass |
| `ui` | `console/`, `packages/ui-core/` | `SPLIT` | Console build and package consumers pass |

### S2 progress

- S2.1 migrated the five `control-plane/` stubs into canonical Control clients,
  health routing and transport facades. Legacy files are compatibility exports
  only; the root remains protected until S5.
- S2.2 migrated the DAG and scheduler prototypes into
  `control/orchestration/`. The two legacy files are compatibility exports only;
  root retirement remains gated on S5.
- S2.3 merged safe unique behavior into `runtime-daemon/`, made the legacy crate
  delegate to the canonical library, and changed incomplete sandbox operations
  from synthetic success to fail-closed errors. Root retirement remains S5.
- S2.4 classified all 121 `execution/` paths. Its only Runtime source,
  `runtime_contract.py`, now re-exports the canonical Control Runtime contract;
  the other 120 deployment, bundle, observability and integration assets remain
  protected for S3/S4.

## Source-of-truth subpaths

```text
schemas/v1/protos/             authored protobuf
schemas/v1/events/             authored event schemas
schemas/v1/json/               authored JSON schemas
shared/generated/python/       generated Python bindings
shared/generated/typescript/   generated TypeScript bindings
shared/generated/rust/         generated Rust bindings
deploy/native/                 systemd, installers, env and profiles
deploy/docker/                 Compose and image definitions
deploy/kubernetes/             Kubernetes assets after Native/Docker parity
```

## CI invariants

1. No new imports from `control-plane`, `rust-runtime`, `database` or `db` in
   canonical source roots.
2. No Console source may resolve a Control or Runtime URL.
3. Gateway has no domain database/ORM dependency or direct data-layer import.
4. Control has no subprocess, shell or host execution call.
5. The legacy-root completion gate stays failing until staged migration removes
   every listed root; documentation mentions are excluded from import checks.
6. S5 deletion still requires human review, recovery evidence and green Native
   plus Quickstart acceptance. A passing path search alone is insufficient.

## Rollback

S1 changes only contracts and architecture checks. Revert its commit to roll
back the gate definition. Changing ownership requires a superseding ADR; do not
silently restore a legacy root as canonical.
