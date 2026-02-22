# Documentation Index

## Architecture and Design
- [ARCHITECTURE](ARCHITECTURE.md)
- [SYSTEM_DESIGN](SYSTEM_DESIGN.md)
- [AGENT_RUNTIME](AGENT_RUNTIME.md)
- [REGISTRY_SYSTEM](REGISTRY_SYSTEM.md)
- [CONTROL_PLANE](CONTROL_PLANE.md)
- [EXECUTION_SANDBOX](EXECUTION_SANDBOX.md)
- [BIGDATA_PIPELINES](BIGDATA_PIPELINES.md)
- [MULTI_TENANT_KERNEL](MULTI_TENANT_KERNEL.md)
- [CONFIG_SYSTEM](CONFIG_SYSTEM.md)
- [POLICIES](POLICIES.md)

## Interfaces
- [API_REFERENCE](API_REFERENCE.md)
- [CLI_REFERENCE](CLI_REFERENCE.md)

## Operations
- [DEPLOYMENT](DEPLOYMENT.md)
- [DEV_GUIDE](DEV_GUIDE.md)
- [CONTRIBUTING](CONTRIBUTING.md)
- [WINDOWS_SETUP](WINDOWS_SETUP.md)

## Migration/Standardization Artifacts
- [../STRUCTURE.md](../STRUCTURE.md) canonical top-level layout
- [../migration/standardization_report.md](../migration/standardization_report.md)
- [../migration/migration_report.md](../migration/migration_report.md)

## Compatibility Notes
- Canonical local compose file: `deploy/compose/docker-compose.local.yml`.
- `aionos_core` implementation lives under `cli/aionos_core` (root wrapper preserved).
- `aionos_control` implementation lives under `control/aionos_control` (legacy import shims preserved).
- `shared/secret_store` is canonical; `os/secret_store` remains as compatibility shim.
