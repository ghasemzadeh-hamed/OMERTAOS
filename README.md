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
docker compose -f docker-compose.local.yml up -d
```

## Runtime Boundary

Python must delegate OS-level execution to runtime daemon via runtime client:
- `control_plane/runtime_client.py`
- gRPC contract: `shared/proto/runtime.proto`
- Rust daemon: `runtime-daemon/`

## Key Planes

- `kernel/` orchestration/router/runtime integration
- `control/` policies/governance/apis
- `data/` rag/vector/adapters
- `services/` service surfaces
- `shared/` contracts/events/observability/event_bus

## Local Endpoints

- Console: `http://localhost:3000`
- Control: `http://localhost:8000`
- Gateway: `http://localhost:8080`
- Runtime daemon (gRPC default): `127.0.0.1:50051`
