# Repository structure

**Document role:** current normative ownership contract.

This document defines the canonical repository topology after the Structure S6
migration. A directory owns one architectural concern; dependencies point
inward toward contracts, never around a service boundary. Historical path
mappings are retained under `docs/migration/` for traceability and are not
alternate implementation owners.

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
| former Runtime and Execution roots | `runtime-daemon/` | Retired in S5 after unique code migration |
| former Control and orchestration roots | `control/` | Retired in S5 after caller migration |
| former root model registry | `registry/models/` | Retired in S5; Registry owns model metadata |
| legacy protobuf aliases | `schemas/v1/protos/` | Edit canonical `.proto` once; regenerate bindings into `shared/generated/` |
| duplicate `schemas/v1` and root schema copies | versioned `schemas/v1/` | Root aliases are temporary and must not diverge |
| former data adapter roots | `data/` | Retired in S5 after adapter consolidation |
| former root Event Bus | `schemas/v1/events/`, `control/ports/`, `integrations/eventbus/` | Retired in S5; contracts, ports and adapters have separate owners |
| former root observability wrappers | `shared/telemetry/`, `integrations/observability/`, `deploy/observability/` | Retired in S5 |
| former Windows Bridge mirror | `integrations/windows-agentic-bridge/` | Retired in S5; Integrations is the sole owner |
| former duplicated deployment material | `deploy/` | Retired in S5; Compose, manifests and scripts have one maintained copy |
| former root UI alias | `console/` or `packages/ui-core/` | Retired in S5 |

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

## Migration status

The precise path mapping and retirement gates are defined in
`docs/migration/canonical-paths.md`. S2 through S5 migrated and retired the
identified duplicate owners; S6 validated the canonical topology and resolved
the S0 unknown roots as documented in
`docs/migration/s6-architecture-validation.md`.

The S6 report is a dated evidence snapshot, not a permanent green status.
Architecture tests must be rerun for every evaluated commit. Legacy content
preserved under `docs/migration/evidence/` is historical input and must not be
reintroduced as an active owner without an ADR, compatibility analysis, and
review.
