# Repository inventory — Structure S0

Date: 2026-07-12

Branch: `capo-structure`

Baseline: `dce93db1`
Scope: tracked files at `HEAD`; working-tree caches and secrets are excluded.

This is a freeze-time inventory, not authorization to move or delete content.
The repository contains 882 tracked paths. No source, database object, generated
artifact, or user data was changed or removed during S0.

## Classification legend

| State | Meaning in S0 |
|---|---|
| `KEEP` | Canonical owner or repository-level asset |
| `MOVE` | Legacy content with one clear canonical destination |
| `MERGE` | Compare and combine with an existing canonical owner |
| `SPLIT` | Contents require routing to multiple owners |
| `DELETE` | Candidate only; deletion requires later proof and approval |
| `GENERATED` | Generated/cache output, not an authoritative source |
| `UNKNOWN` | Ownership must be resolved before any mutation |

## Canonical roots

| Root | Tracked paths | State | Owner / note |
|---|---:|---|---|
| `console/` | 230 | `KEEP` | Product UI |
| `gateway/` | 26 | `KEEP` | Public API boundary |
| `control/` | 21 | `KEEP` | Orchestration and decisions |
| `runtime-daemon/` | 22 | `KEEP` | Privileged execution |
| `data/` | 17 | `KEEP` | Persistence and data adapters |
| `registry/` | 14 | `KEEP` | Agent/model/prompt metadata |
| `policies/` | 4 | `KEEP` | Governance and capability policy |
| `schemas/` | 36 | `MERGE` | Canonical source must converge under `schemas/v1/` |
| `shared/` | 10 | `KEEP` | Generated clients and shared primitives |
| `deploy/` | 92 | `MERGE` | Canonical deployment owner; absorb duplicate assets |
| `integrations/` | 39 | `MERGE` | Canonical external integration owner |
| `packages/` | 5 | `KEEP` | Shared packages and SDKs |
| `tests/` | 29 | `KEEP` | Architecture, contract and acceptance evidence |
| `docs/` | 16 | `KEEP` | Architecture and migration records |
| `scripts/` | 6 | `SPLIT` | Keep repository maintenance only; route deploy logic |

## Legacy and transitional roots

| Root | Tracked paths | State | Intended disposition |
|---|---:|---|---|
| `control-plane/` | 5 | `MERGE` | Compare with `control/` |
| `orchestration/` | 2 | `MOVE` | Route orchestration logic to `control/` |
| `rust-runtime/` | 31 | `MERGE` | Compare with `runtime-daemon/` |
| `execution/` | 121 | `SPLIT` | Runtime, deployment, integration and bundle content |
| `database/` | 16 | `MERGE` | Compare with `data/` |
| `db/` | 9 | `MERGE` | Route interfaces/adapters to `data/` |
| `models/` | 14 | `MERGE` | Metadata to `registry/models/`; providers elsewhere |
| `eventbus/` | 4 | `SPLIT` | Contracts, ports and implementations have distinct owners |
| `observability/` | 9 | `SPLIT` | Shared telemetry, integrations and deploy assets |
| `docker/` | 1 | `MOVE` | Consolidate in `deploy/docker/` |
| `infra/` | 4 | `MOVE` | Consolidate native assets in `deploy/native/` |
| `agents/` | 1 | `SPLIT` | Metadata, logic, SDK and payload ownership unresolved |
| `protos` | 1 symlink | `MOVE` | Replace references with `schemas/v1/protos/` after validation |
| `ui` | 1 symlink | `MOVE` | Replace with `console/` or `packages/ui-core/` references |

## Other tracked root directories

| Root | Tracked paths | State | Note |
|---|---:|---|---|
| `.github/` | 3 | `KEEP` | CI and repository automation |
| `algorithms/` | 1 | `UNKNOWN` | Placeholder/package ownership needs evidence |
| `cluster/` | 5 | `UNKNOWN` | Decide control metadata versus runtime execution |
| `config/` | 6 | `SPLIT` | Route service/deployment configuration by owner |
| `core/` | 4 | `SPLIT` | Inspect systemd and historical core ownership |
| `desktop-shell/` | 37 | `UNKNOWN` | Product/integration ownership needs architecture decision |
| `domain/` | 3 | `UNKNOWN` | Compare against canonical control/shared contracts |
| `migration/` | 1 | `GENERATED` | Tracked build log; candidate recorded separately |

`process-analytics` is a tracked root symlink and remains `UNKNOWN` until its
target, consumers and ownership are proven. Root compose/install wrappers and
repository configuration files remain `KEEP` for now; consolidation is a later
phase and must preserve Quickstart compatibility.

## Freeze gate

- Every tracked root directory or root symlink has a status.
- `UNKNOWN` means blocked from mutation, not implicitly disposable.
- No file was moved, merged or deleted in S0.
- Permanent deletion remains closed until the required architecture, Native and
  Quickstart gates pass.
