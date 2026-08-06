# OMERTAOS Project Context

## Project Type

Hybrid Agent OS / AI Agent Operating Layer / Distributed Multi-Agent Platform.

## Version Focus

- OMERTAOS Version: AION
- Branch focus: the currently checked-out branch; never switch automatically
- Execution strategy: preserve both Native and Docker Quickstart paths
- Task focus: the current user request, not a historical backlog
- Current ownership source: `docs/migration/canonical-paths.md`

Snapshot as of 2026-07-13: the CAPO seven-phase ledger is complete on its CAPO
workflow, while the `capo-structure` history has completed S3.1 through S3.4 and
records S3.5 through S3.7 as pending. Always verify Git and the canonical-paths
contract before using this snapshot; do not start a pending phase unless the
user explicitly requests it.

## Stack

- Console: Next.js / TypeScript / React / Tailwind / Prisma / NextAuth
- Gateway: Node.js / Fastify / gRPC / Redis / JWT / OpenTelemetry / Helmet / CORS / WebSocket / SSE
- Control Plane: Python / FastAPI / gRPC adapter
- Runtime: Rust Runtime Daemon
- Data Layer: Postgres, Redis, MongoDB, Qdrant, MinIO
- Event / Policy / Observability: eventbus, policies, observability, audit
- Models: model profiles under models/ and registry/models/ until canonicalization

## Target Architecture

Console / Next.js
    -> Gateway / Fastify
    -> Control Plane / Python
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
- control-plane/
- runtime-daemon/
- rust-runtime/
- data/
- database/
- registry/
- models/
- schemas/
- policies/
- eventbus/
- observability/
- orchestration/
- integrations/windows-agentic-bridge/
- execution/

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

- control/ should become canonical Control Plane.
- control-plane/ is legacy or compatibility source for now.
- runtime-daemon/ is canonical runtime layer.
- rust-runtime/ is legacy or complementary source for now.
- kernel/ may not exist; references to it must not break quickstart.
- Do not perform heavy folder migration until local setup and quickstart are stable.
- Do not delete duplicate sources before import/reference/history checks.

## Acceptance Criteria For Current Phase

- Doctor action reports missing/available tools.
- Native Setup installs safe dependencies without starting long-running services.
- Docker Validate runs:
  docker compose -f docker-compose.quickstart.yml config
- Docker Build can be attempted manually.
- Console, Gateway, Control paths are preserved.
- No critical folder is deleted.
