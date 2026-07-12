# Repository structure

This document defines the target repository topology. A directory owns one architectural concern; dependencies point inward toward contracts, never around a service boundary.

```text
OMERTAOS/
├── console/          # Next.js UI
├── gateway/          # Fastify external API
├── control/          # Python orchestration
├── runtime-daemon/   # Rust privileged execution
├── data/             # persistence and retrieval adapters
├── registry/         # agent and model catalogs
├── policies/         # policy definitions and evaluator adapters
├── schemas/          # versioned source contracts
├── shared/           # generated clients and shared primitives
├── deploy/           # deployment and operations assets
├── tests/            # cross-service and acceptance tests
└── integrations/     # external-system adapters
```

## Ownership and source of truth

| Directory | Responsibility | Source of truth |
|---|---|---|
| `console/` | Presentation, browser session, API client | UI routes/components and Console configuration |
| `gateway/` | Authentication, admission control, public API, streams | Public HTTP contract implementation; schemas remain in `schemas/` |
| `control/` | Task state, planning, scheduling, routing, aggregation | Orchestration behavior and lifecycle transitions |
| `runtime-daemon/` | Sandbox, process execution, resource/capability enforcement | All privileged execution behavior |
| `data/` | Store adapters, transactions, caching and RAG | Persistence interfaces and mapping rules; schemas do not live here |
| `registry/` | Agent/model registration, lookup and version resolution | Registry service behavior; metadata files reside under its owned subtrees |
| `policies/` | RBAC/CBAC rules and policy bundles | Human-authored authorization policy |
| `schemas/` | Protobuf, JSON Schema and event contracts | Canonical contract definitions by major version |
| `shared/` | Generated bindings, common IDs/errors/telemetry | Generated output and deliberately stable primitives only |
| `deploy/` | Compose, Kubernetes, CI and install/restore assets | Deployment topology and operational procedure |
| `tests/` | Cross-layer, contract, integration, load and acceptance tests | System-level verification; unit tests may be colocated with services |
| `integrations/` | MCP, OS and third-party boundary adapters | Integration-specific translation; no core orchestration |

## Boundary rules

1. Each layer has a single responsibility. UI presents; Gateway admits; Control decides; Runtime executes; Data persists.
2. Console calls Gateway only. Direct Console → Control, Runtime, registry database, or data-store access is forbidden.
3. Gateway may call Control through versioned gRPC/HTTP clients but contains no planning or execution logic.
4. Control may call Runtime only through versioned gRPC and may access data only through `data/` interfaces.
5. Runtime does not select agents/models, interpret business policy, or write Control tables. It verifies and enforces supplied grants.
6. Services import contracts/generated bindings from `schemas/`/`shared/`; they do not import another service's internals.
7. Events are facts in past tense, versioned, tenant-scoped, idempotent, and carry correlation/causation IDs.
8. `integrations/` consumes public interfaces and cannot become an alternate Gateway.

The allowed dependency direction is `console → gateway → control → runtime-daemon`, while all services may depend on `schemas` and narrowly scoped `shared` primitives. Control depends on `data`, `registry`, and policy interfaces; those domains must not depend on Control implementation modules.

## Duplicate elimination

The current tree contains migration-era alternatives. New work uses the canonical owners above.

| Legacy path | Canonical destination | Rule |
|---|---|---|
| `rust-runtime/`, execution code under `execution/` | `runtime-daemon/` | Migrate unique code; do not add new runtime behavior to legacy paths |
| `control-plane/`, orchestration in `kernel/` or `orchestration/` | `control/` | Move behavior behind Control interfaces |
| root `models/` | `registry/models/` | Registry owns model metadata; retain compatibility reads only during migration |
| legacy protobuf aliases | `schemas/v1/protos/` | Edit canonical `.proto` once; regenerate bindings into `shared/generated/` |
| duplicate `schemas/v1` and root schema copies | versioned `schemas/v1/` | Root aliases are temporary and must not diverge |
| `database/`, `db/` | `data/` | Consolidate adapters; deployment state remains in `deploy/` |
| duplicated deployment material under `execution/` or `docker/` | `deploy/` | Compose/manifests/scripts have one maintained copy |
| `ui/` | `console/` or `packages/ui-core/` | Product UI belongs to Console; reusable UI primitives to the package |

Deletion requires import/caller migration, compatibility tests, and an upgrade note. Architecture tests in `tests/architecture/` should reject new imports into legacy roots.

## Additional canonical owners

| Directory | Responsibility | Source of truth |
|---|---|---|
| `packages/` | Reusable UI primitives and agent SDK | Versioned package interfaces; no product pages |
| `scripts/` | Repository maintenance | Thin maintenance commands; no independent deployment logic |
| `docs/` | Decisions and operator/developer guidance | Accepted ADRs and current architecture contracts |

Gateway may use Redis only for rate limiting, idempotency and ephemeral
coordination; it must not access domain persistence or own database schemas.
Control must not spawn processes or perform host-side effects. Only a versioned
Runtime client crosses that boundary.

## Migration freeze

The precise path mapping and retirement gates are defined in
`docs/migration/canonical-paths.md`. Until the corresponding migration phase
passes, legacy roots are read-only migration inputs: fixes needed to preserve an
existing recovery path require explicit review, while new capabilities are
forbidden. An `UNKNOWN` item from the S0 inventory cannot be moved or deleted.

The Structure migration gate is intentionally failing at S1 because legacy
roots and a direct Console-to-Control health path still exist. This is recorded
debt, not permission to weaken or skip the gate. S2 through S5 remove violations;
S6 proves the final topology.
