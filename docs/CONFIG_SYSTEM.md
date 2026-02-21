# CONFIG_SYSTEM

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
