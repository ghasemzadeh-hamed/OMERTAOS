# OMERTAOS

OMERTAOS is an enterprise-grade distributed AI-agent platform that combines a FastAPI control plane, registry-driven model orchestration, Rust execution isolation, big-data pipelines, and a multi-tenant kernel runtime.

## Project Overview
OMERTAOS standardizes how autonomous agents are built, governed, deployed, and observed across development, staging, and production environments.

## Vision & Mission
- **Vision:** provide a secure operating substrate for scalable autonomous AI systems.
- **Mission:** unify control, execution, governance, and deployment under one consistent architecture.

## System Capabilities
- Async FastAPI control plane and orchestration APIs
- Registry-backed model and agent metadata resolution
- Rust execution sandbox for isolated module execution
- Multi-tenant kernel policy enforcement
- BigData pipelines for streaming and batch analytics
- CLI + Console interfaces for operators and developers
- Docker, Compose, and Helm deployment support

## High-Level Architecture Diagram
```mermaid
flowchart LR
  CLI[CLI] --> CP[Control Plane
FastAPI]
  Console[Console UI] --> CP
  CP --> Registry[Registry API
ai_registry]
  CP --> Kernel[Kernel / Tenancy]
  Kernel --> Exec[Rust Execution Sandbox]
  CP --> DB[(MongoDB / Storage)]
  BigData[BigData Pipelines] --> DB
  CP --> Policies[Policy Engine]
```

## Directory Structure (Canonical)
```text
/core /agents /control /registry /config /schemas /execution
/db /bigdata /cli /console /kernel /policies /shared
/deploy /tests /tools
```

## Recent Architecture Standardization Notes
- `config` and `registry` are root-level canonical Python modules (the legacy `omertaos/*` package scaffold has been removed).
- `aionos_core` implementation is now in `cli/aionos_core` with compatibility wrappers at `aionos_core/*`.
- `aionos_control` implementation is now in `control/aionos_control` with compatibility wrappers retained.
- legacy `os/secret_store` has been distributed to `shared/secret_store` with compatibility shims.
- local compose canonical path is `deploy/compose/docker-compose.local.yml` (root `docker-compose.local.yml` remains as compatibility symlink).

## Key Components Overview
- **Control Plane:** API routing, orchestration, async workers.
- **Agents:** runtime agents and algorithm modules.
- **Registry:** canonical metadata for models, agents, and locks.
- **Execution:** isolated Rust runtime modules.
- **Kernel:** multi-tenant runtime + policy enforcement.
- **BigData:** ETL/streaming and decision-support pipelines.

## Installation
See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [docs/DEV_GUIDE.md](docs/DEV_GUIDE.md).

## Quick Start
```bash
git clone <repo-url>
cd OMERTAOS
./install.sh --profile user --local
```

## Documentation Links
- [Architecture](docs/ARCHITECTURE.md)
- [System Design](docs/SYSTEM_DESIGN.md)
- [Control Plane](docs/CONTROL_PLANE.md)
- [Registry System](docs/REGISTRY_SYSTEM.md)
- [Execution Sandbox](docs/EXECUTION_SANDBOX.md)
- [API Reference](docs/API_REFERENCE.md)
- [CLI Reference](docs/CLI_REFERENCE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Whitepaper](docs/WHITEPAPER.md)

## License
See [LICENSE](LICENSE).
