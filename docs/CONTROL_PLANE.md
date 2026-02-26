# CONTROL_PLANE

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## FastAPI Surface
The control plane exposes health, models, datasets, metrics, services, packages, backup/update, registry, and agent orchestration endpoints.

## Orchestrator Logic
- Request validation and auth checks
- Registry/config resolution
- Task scheduling and worker dispatch
- State persistence and event publication

## Task Scheduling
- Async worker loops for background operations
- Request-context aware scheduling with tenancy metadata

## Async Handling
- Non-blocking HTTP APIs
- Startup/shutdown hooks for worker lifecycle
- Metrics and health probes for runtime readiness

## Control Plane Scope

Control plane remains Python-only for API/policy/orchestration concerns and delegates execution/isolation to runtime daemon.
