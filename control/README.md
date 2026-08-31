# Control Plane

**Document role:** component ownership contract and target processing model.
The Python service and Runtime-client boundary are implemented as a prototype;
the complete lifecycle below requires end-to-end validation before it is
reported as system behavior.

The Python Control Plane is OMERTAOS's orchestration authority. It owns task lifecycle state, planning, agent resolution, model routing, contextual policy evaluation, scheduling, retry decisions, and result aggregation. It does not run arbitrary commands; privileged execution is delegated to the Rust Runtime Daemon over gRPC.

## APIs

- Task submission creates a durable task and returns its identifier/state.
- Task status exposes authorized lifecycle, attempts, and result references.
- Agent execution resolves a registered agent version and schedules its bounded plan.

An async FastAPI-compatible HTTP surface may provide health and administrative compatibility endpoints; service-to-service task operations use generated gRPC contracts. Handlers remain non-blocking and delegate CPU-heavy work to bounded executors.

Current HTTP prototype endpoints include:

- `GET /v1/config/status` for the effective and pending router configuration;
- `POST /v1/config/propose`, `/apply`, and `/revert` for authenticated configuration changes;
- `/v1/network/proxies` for authenticated proxy profile management;
- `/v1/runtime/nodes` and `/v1/runtime/schedule` for the minimal node registry and scheduler;
- `GET /v1/runtime/audit/{task_id}` for a Gateway-service-token-authenticated,
  tenant-scoped Runtime scheduling and dispatch trail with bounded cursor
  pagination;
- `/health`, `/v1/health`, and `/v1/models` for source-backed status and model metadata.

Configuration state is stored in the additive `control_configuration` table.
Runtime schedule/dispatch events are stored in the additive
`runtime_audit_events` table without task payloads, result text, idempotency
keys, or credentials. Apply the current Control schema with
`python -m control.app.network.migrate`; use `--check` for a read-only gate.

## Pipeline

```text
input → contract validation → durable task → agent/model resolution → planning
      → policy evaluation → scheduling → runtime dispatch → event ingestion
      → result aggregation → persistence → terminal event
```

The Control Plane accesses Postgres, MongoDB, Redis/Streams, Qdrant, and MinIO only through Data Layer adapters. Registry and policy access use explicit interfaces. Every task and attempt carries tenant, correlation, schema, and policy/routing-version metadata.

## Runtime communication

Dispatch RPCs include task/attempt IDs, lease fencing token, deadline, immutable plan reference, input/artifact references, and a signed capability grant. Runtime responses and events are idempotently applied. Control never asks Runtime to infer permissions.

## Docker

```bash
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up --build control
curl http://localhost:8000/health
```

Important configuration includes `AION_CONTROL_POSTGRES_DSN`, `AION_CONTROL_MONGO_DSN`, `AION_CONTROL_REDIS_URL`, `AION_CONTROL_QDRANT_URL`, `AION_CONTROL_MINIO_*`, `AION_CONTROL_MODELS_DIRECTORY`, `AION_CONTROL_POLICIES_DIRECTORY`, `TENANCY_MODE`, the Runtime gRPC endpoint, and `AION_GATEWAY_ADMIN_TOKEN` for authenticated Gateway-owned admin calls. Production credentials must come from the configured secret provider.

When the development-only local proxy-secret fallback is explicitly enabled,
set `AION_CONTROL_LOCAL_SECRET_KEY` to a base64-encoded AES key. Local proxy
secrets are encrypted and authenticated on disk; the fallback fails closed when
this key is absent. Production should use the configured external secret
provider instead.

The Runtime client reads `AION_RUNTIME_ENDPOINT` (default
`127.0.0.1:50051`) and uses the generated gRPC transport. The canonical facade
is fail-closed: transport errors are reported as `RuntimeTransportUnavailable`,
every request has a positive timeout, and Control never executes the command
locally or reports synthetic success.
