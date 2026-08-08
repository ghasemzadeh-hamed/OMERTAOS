<p align="center">
  <img src="https://img.shields.io/badge/OMERTAOS-AION-6D5DFB?style=for-the-badge" />
  <img src="https://img.shields.io/badge/OMERTAOS-CAPO-6D5DFB?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Type-Hybrid%20Agent%20OS-4B5563?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Architecture-Agentic%20OS-7C3AED?style=for-the-badge" />
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" />
  </a>
  <img src="https://img.shields.io/badge/aion-core-v0.2.0-indigo" />
  <img src="https://img.shields.io/badge/console-v0.1.0-black" />
  <img src="https://img.shields.io/badge/gateway-v0.1.0-gray" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11--3.12-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Control-FastAPI-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Runtime-Rust%20Daemon-000000?logo=rust&logoColor=white" />
  <img src="https://img.shields.io/badge/Console-Next.js%2014-000000?logo=nextdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/Gateway-Fastify-000000?logo=fastify&logoColor=white" />
  <img src="https://img.shields.io/badge/Quickstart-Docker%20Compose-2496ED?logo=docker&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/Hamedghz/OMERTAOS?style=social" />
  <img src="https://img.shields.io/github/forks/Hamedghz/OMERTAOS?style=social" />
  <img src="https://img.shields.io/github/issues/Hamedghz/OMERTAOS" />
  <img src="https://img.shields.io/github/issues-pr/Hamedghz/OMERTAOS" />
  <img src="https://img.shields.io/github/last-commit/Hamedghz/OMERTAOS/AION" />
</p>

<p align="center">
  <a href="https://github.com/Hamedghz/OMERTAOS/actions/workflows/release.yml">
    <img src="https://github.com/Hamedghz/OMERTAOS/actions/workflows/release.yml/badge.svg" />
  </a>
</p>

# OMERTAOS

Hybrid Agent Operating System:
- Python Control Plane (AI orchestration, governance, APIs)
- Rust Runtime Daemon (OS isolation, sandboxed execution, command/runtime boundary)

## Quick Install

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./quick-install.sh
```

Alternative local development startup:

```bash
docker compose --project-directory . -f deploy/docker/compose/local.yml up -d
```

## Runtime Boundary

Python must delegate OS-level execution to runtime daemon via runtime client:
- target canonical client: `control/runtime/`
- gRPC contracts: `schemas/v1/protos/`
- Rust daemon: `runtime-daemon/`

## Canonical Planes

- `control/` orchestration, scheduling, governance and APIs
- `runtime-daemon/` privileged execution and sandbox enforcement
- `data/` persistence, RAG, memory and adapters
- `registry/` agent, model and prompt metadata
- `policies/` policy definitions and evaluator interfaces
- `schemas/` source contracts; `shared/` generated clients and stable primitives

The migration-era service, data, model and deployment roots were retired in
Structure S5. New behavior belongs only to the canonical planes listed above;
historical path mappings remain documented under `docs/migration/`.

## Redesign and recovery

- [Structure S6 validation](docs/migration/s6-architecture-validation.md)
- [Canonical design](docs/architecture/aion-canonical-design.md)
- [Capability recovery plan](docs/migration/aion-capability-recovery.md)
- [ADR 0001: canonical ownership](docs/adr/0001-canonical-aion-ownership.md)

## Local Endpoints

- Console: `http://localhost:3000`
- Control: `http://localhost:8000`
- Gateway: `http://localhost:8080`
- Runtime daemon (gRPC default): `127.0.0.1:50051`
