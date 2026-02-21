# CONTROL_PLANE

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
