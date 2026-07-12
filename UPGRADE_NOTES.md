# Upgrade Notes

## Hybrid Runtime Migration

Current architecture uses:
- Python control-plane orchestration and policy layers.
- Rust runtime daemon for OS-boundary execution.

### Breaking expectations

- Direct Python process execution paths are deprecated in favor of runtime daemon RPC delegation.
- Isolation/resource operations are routed through runtime client and runtime daemon.

### Required components

- `runtime-daemon` binary/service
- canonical `schemas/v1/protos/runtime.proto` contract compatibility
- `control_plane/runtime_client.py` configured endpoint
