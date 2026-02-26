# CONFIG_SYSTEM

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Unified Configuration API
The architecture standard is a unified config loader surface:
- `load_env()`
- `get_config(key)`
- `load_scope(scope_name)`

## Configuration Domains
- environment variables
- profile overlays
- deployment-scoped manifests
- tenant-specific overrides

## Operational Guidance
- Avoid direct ad-hoc env reads in runtime code.
- Use scoped config loading for deterministic behavior.
