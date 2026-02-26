# EXECUTION_SANDBOX

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Rust Isolation
Rust modules in `execution/` provide a constrained execution substrate for agent workloads.

## Execution Safety
- Resource-limited and contract-driven invocation
- Minimized host surface area
- Clear boundary between orchestration and runtime execution

## Performance Characteristics
- Low-overhead native execution
- Predictable memory and CPU profiles for bounded tasks
- Compatible with multi-worker control dispatch

## Sandbox Ownership

Sandbox enforcement is owned by `runtime-daemon/src/sandbox/*` and called from Python through `control_plane/runtime_client.py`.

