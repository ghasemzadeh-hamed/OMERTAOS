# Docker installation

Run AION-OS inside containers for local development, CI pipelines, or lightweight demos. Disk operations are skipped; profile rendering and service orchestration continue to use the same wizard.

## Prerequisites

- Docker Engine 24 or newer
- Docker Compose V2 (`docker compose` CLI)
- 8 GB RAM minimum

## Steps

1. Clone the repository and copy `.env` from the template:
   ```bash
   cp config/templates/.env.example .env
   ```
2. Edit `.env` and set `AION_PROFILE=user|pro|enterprise`.
3. Start the base stack:
   ```bash
   docker compose up --profile base -d
   ```
4. To enable extra services (MLflow, observability, etc.), add the profile flag:
   ```bash
   docker compose --profile enterprise up -d
   ```
5. Open `http://localhost:3000/wizard` to walk through the installer.
6. Storage actions show previews only; driver installs run in dry-run mode with logs in `/var/log/aionos-installer.log` inside the installer container.
7. Verify the console at `http://localhost:3000/console` and the control plane health endpoints (`docker compose logs control`).
8. Tear down with `docker compose down`.

## Tips

- Use `docker compose logs -f bridge` to watch hardware probe output while testing.
- The offline cache is mapped from `core/iso/cache/` if you need to ship pre-approved packages.
- To build reproducible images, follow [`docs/release.md`](../release.md) for SBOM and signing steps.
