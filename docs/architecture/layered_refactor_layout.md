# OMERTAOS Layered Architecture Refactor

This document defines the target architecture and module layout to enforce strict boundaries and remove duplicated concerns.

## Target Directory Structure

```text
omertaos/
├─ kernel/                  # lifecycle, boot, shutdown
├─ orchestration/           # control-plane orchestration, policy selection, registry client
├─ runtime/                 # execution, worker runtime, sandbox boundary
├─ interface/               # gateway, cli, console adapters
├─ agents/                  # agent packages and manifests
├─ contracts/               # unified schemas/shared/protos
│  ├─ schemas/
│  ├─ shared/
│  └─ protos/
└─ observability/           # metrics, tracing, telemetry exporters
```

## Dependency Direction (No Cycles)

Allowed dependencies only flow downward:

- `interface -> orchestration -> runtime -> kernel`
- `agents -> contracts`
- `interface|orchestration|runtime|kernel -> contracts`
- `interface|orchestration|runtime|kernel|agents -> observability`

Forbidden examples:

- `runtime -> interface`
- `kernel -> orchestration`
- `contracts -> any layer`

## Registry Consolidation

- Registry ownership is centralized under `orchestration/registry_service`.
- Runtime reads registry data only through service interfaces/contracts.
- Legacy registry wrappers remain only for backward compatibility during migration.

## Policy Boundary

- Gateway performs request validation only (shape/auth/input checks).
- Runtime execution boundary performs policy enforcement (resource limits, isolation, execution permissions).

## Runtime Refactor Summary

Implemented in the `execution` crate:

- `runtime/sandbox.rs`: trait-based sandbox abstraction (`Sandbox`) with `OsIsolatedSandbox`.
- Linux isolation: seccomp strict mode + cgroup process attachment.
- Structured tracing instrumentation for execution paths.
- `runtime/queue.rs`: queue abstraction (`TaskQueue`) with in-memory adapter.
- `runtime/worker.rs`: worker consumes queue and sandbox via traits (decoupled execution).

## Contracts Unification Plan

Current source locations:

- `schemas/`
- `shared/`
- `schemas/protos/`

Migration target:

- `contracts/schemas/`
- `contracts/shared/`
- `contracts/protos/`

## Observability Layer

- `execution/src/observability.rs` initializes structured tracing.
- Service-level tracing should include task id, agent id, policy decision, and isolation mode.

