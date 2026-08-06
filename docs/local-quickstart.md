# Local Docker quickstart

OMERTAOS provides two canonical local Compose entry points. `deploy/docker/compose/quickstart.yml` is the primary, minimal stack. `deploy/docker/compose/local.yml` exposes additional infrastructure ports for development and keeps Vault behind an optional profile. Use `--project-directory .` from the repository root so build contexts and bind mounts remain repository-relative.

## Requirements

- Docker Desktop on Windows/macOS, or Docker Engine with Compose v2 on Linux
- At least 8 GB of available memory
- Free host ports 3000, 8000, 8080, and loopback-only 50051 for quickstart
- For the extended local stack, also free ports 5432, 6379, 27017, 6333, 9000, and 9001

Confirm that the Docker daemon is running before starting:

```bash
docker version
docker compose version
```

## Environment setup

Create a local environment file from the development defaults:

```bash
cp dev.env .env
```

On PowerShell:

```powershell
Copy-Item dev.env .env
```

The checked-in values are local placeholders only. Do not use them in production or expose the development services publicly.

## Quickstart

```bash
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml config
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml build
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml up -d
docker compose --project-directory . -f deploy/docker/compose/quickstart.yml ps
```

Expected host ports:

| Service | URL |
|---|---|
| Console | `http://localhost:3000` |
| Control | `http://localhost:8000` |
| Gateway | `http://localhost:8080` |
| Runtime gRPC | `127.0.0.1:50051` |

Runtime readiness is checked from inside its container before Control starts.
Control readiness uses Python's standard-library HTTP client, so its image does
not install an extra system curl package solely for health checks.

Check health with:

```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/v1/health
curl -f http://localhost:8080/health
curl -f http://localhost:3000/
```

Stop the stack with `docker compose --project-directory . -f deploy/docker/compose/quickstart.yml down`.

## Extended local stack

The canonical extended local entry is:

```bash
docker compose --project-directory . -f deploy/docker/compose/local.yml config
docker compose --project-directory . -f deploy/docker/compose/local.yml up -d
```

Vault is optional and starts only when explicitly selected:

```bash
docker compose --project-directory . -f deploy/docker/compose/local.yml --profile vault up -d
```

The historical `kernel/` service is disabled because that directory and Dockerfile are not present. The canonical `runtime-daemon/` runs as the `runtime` service and exposes its gRPC endpoint on loopback port 50051 for local development.

## Common errors

### Missing Dockerfile

Run `docker compose ... config` and verify that each build uses the repository root as its context and an existing service Dockerfile. Do not create an empty service solely to satisfy Compose.

### Missing environment values

Recreate `.env` from `dev.env`. `docker compose ... config` shows the resolved values and reports unset variables.

### Port already in use

Stop the process or older Compose project using 3000, 8000, 8080, or 50051. Use `docker compose --project-directory . -f deploy/docker/compose/quickstart.yml down` to stop an earlier OMERTAOS stack.

### Kernel path not found

Use `deploy/docker/compose/quickstart.yml` or `deploy/docker/compose/local.yml`; these entry points do not reference the removed `kernel/` path. The primary quickstart includes the canonical Rust runtime.

### Gateway cannot reach Control

Inside containers the Gateway must use `http://control:8000`, never `localhost:8000`. Inspect `docker compose ... logs control gateway` and confirm the Control healthcheck is healthy.

### Console cannot reach Gateway

Browser code uses `NEXT_PUBLIC_GATEWAY_URL=http://localhost:8080`. Server-side Console code uses `GATEWAY_URL=http://gateway:8080`. Mixing these two address spaces causes connection failures.
