# Control Plane

The Python Control Plane is OMERTAOS's orchestration authority. It owns task lifecycle state, planning, agent resolution, model routing, contextual policy evaluation, scheduling, retry decisions, and result aggregation. It does not run arbitrary commands; privileged execution is delegated to the Rust Runtime Daemon over gRPC.

## APIs

- Task submission creates a durable task and returns its identifier/state.
- Task status exposes authorized lifecycle, attempts, and result references.
- Agent execution resolves a registered agent version and schedules its bounded plan.

An async FastAPI-compatible HTTP surface may provide health and administrative compatibility endpoints; service-to-service task operations use generated gRPC contracts. Handlers remain non-blocking and delegate CPU-heavy work to bounded executors.

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
docker compose -f docker-compose.quickstart.yml up --build control
curl http://localhost:8000/health
```

Important configuration includes `AION_CONTROL_POSTGRES_DSN`, `AION_CONTROL_MONGO_DSN`, `AION_CONTROL_REDIS_URL`, `AION_CONTROL_QDRANT_URL`, `AION_CONTROL_MINIO_*`, `AION_CONTROL_MODELS_DIRECTORY`, `AION_CONTROL_POLICIES_DIRECTORY`, `TENANCY_MODE`, and the Runtime gRPC endpoint. Production credentials must come from the configured secret provider.

The Runtime client reads `AION_RUNTIME_ENDPOINT` (default
`127.0.0.1:50051`). The canonical facade is fail-closed: callers must install a
versioned generated transport before execution, and every request has a positive
timeout. It never executes a command locally or reports synthetic success.
