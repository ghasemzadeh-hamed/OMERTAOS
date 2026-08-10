# OMERTAOS Project Context

## Project Type

Hybrid Agent OS / AI Agent Operating Layer / Distributed Multi-Agent Platform.

## Version Focus

- OMERTAOS Version: AION
- Branch focus: the currently checked-out branch; never switch automatically
- Execution strategy: preserve both Native and Docker Quickstart paths
- Task focus: the current user request, not a historical backlog
- Current ownership source: `docs/migration/canonical-paths.md`

Snapshot as of 2026-08-10: Structure phases S0-S6 are represented in Git
history and the retired migration roots are absent. Always verify the current
branch, working tree, CI evidence and `docs/migration/canonical-paths.md` before
claiming a Gate passed. Do not infer authorization for a new phase from this
snapshot.

## Stack

- Console: Next.js / TypeScript / React / Tailwind / Prisma / NextAuth
- Gateway: Node.js / Fastify / gRPC / Redis / JWT / OpenTelemetry / Helmet / CORS / WebSocket / SSE
- Control: Python / FastAPI / gRPC adapter
- Runtime: Rust Runtime Daemon
- Data Layer: Postgres, Redis, MongoDB, Qdrant, MinIO
- Event / Policy / Observability: canonical schemas, Control ports, integrations, policies and shared telemetry
- Models: immutable model profiles under `registry/models/`

## Target Architecture

Console / Next.js
    -> Gateway / Fastify
    -> Control / Python
    -> Runtime Daemon / Rust
    -> Agent Execution / Sandbox / Tools

Data Layer:
Postgres + Redis + Mongo + Qdrant + MinIO

Policy / Registry:
Policies + Model Profiles + Agent Registry + Schemas

## Main Modules

- console/
- gateway/
- control/
- runtime-daemon/
- data/
- registry/
- schemas/
- policies/
- integrations/windows-agentic-bridge/
- shared/
- deploy/

## Historical Priorities

The priority lists below describe the original CAPO stabilization context. They
are reference material, not standing authorization to execute work.

### P0

- Protect critical folders from deletion.
- Stabilize CAPO native setup.
- Fix Docker/Compose build pathing.
- Ensure control, gateway, and console can start.
- Ensure invalid kernel references do not block quickstart.
- Add or preserve health endpoints:
  - http://localhost:8000/health
  - http://localhost:8000/v1/health
  - http://localhost:8080/health
  - http://localhost:3000

### P1

- Canonicalize Model Registry later.
- Canonicalize data adapters later.
- Unify schemas/protos later.
- Merge integrations/windows-agentic-bridge and execution/windows-agentic-bridge later.

### P2

- Implement AION modules:
  - Agentic Workflow Orchestration
  - MLOps / LLMOps
  - RAG
  - Multimodal System Integration
  - AI Cybersecurity
  - AI Governance
  - No-Code AI Automation Builder

## Known Constraints

- `control/` is the canonical decision and orchestration owner.
- `runtime-daemon/` is the canonical execution boundary.
- Retired-root names are permitted only in the centralized architecture fixture
  and historical ADR/migration evidence.
- Native and Docker acceptance require their own current runtime evidence.
- Do not restore retired roots, bypass the canonical service chain, or infer
  deploy authority from a passing Structure test.

## Acceptance Criteria For Current Phase

- Doctor action reports missing/available tools.
- Native Setup installs safe dependencies without starting long-running services.
- Docker validation renders the canonical Compose definitions under `deploy/docker/`.
- Docker Build can be attempted manually.
- Console, Gateway, Control and Runtime boundaries are preserved.
- No canonical folder is deleted or duplicated by a retired owner.
