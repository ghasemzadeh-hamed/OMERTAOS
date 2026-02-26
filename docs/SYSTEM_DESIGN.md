# SYSTEM_DESIGN

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Design Principles
- Deterministic orchestration
- Isolation-first execution
- Policy-driven autonomy
- Deploy-anywhere architecture

## Core Runtime Model
```mermaid
sequenceDiagram
  participant C as Client (CLI/Console)
  participant P as Control Plane
  participant R as Registry
  participant K as Kernel
  participant E as Execution Sandbox
  participant D as Data Stores

  C->>P: Submit task
  P->>R: Resolve model+agent
  P->>K: Build execution context
  K->>E: Execute isolated workload
  E-->>K: Result + metrics
  K-->>P: Policy-filtered output
  P->>D: Persist state/telemetry
  P-->>C: Response
```

## Reliability and Safety
- Async task workers with retry boundaries
- Health endpoints and metrics surfaces
- Registry lock based reproducibility
- Policy enforcement before execution dispatch
