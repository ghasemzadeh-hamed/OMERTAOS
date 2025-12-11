# Docker installation

Run AION-OS inside containers for local development, CI pipelines, or lightweight demos. Disk operations are skipped; profile rendering and service orchestration continue to use the same wizard components.

## Prerequisites

- Docker Engine 24 or newer
- Docker Compose V2 (`docker compose` CLI)
- 8 GB RAM minimum

## Steps

1. Copy `dev.env` to `.env` (or run `./quick-install.sh` to do this automatically and generate development certs).
2. Start the quickstart stack with bundled databases and storage:
   ```bash
   docker compose -f docker-compose.quickstart.yml up -d
   ```
3. Watch health endpoints until they return HTTP 200:
   - Control: http://localhost:8000/healthz
   - Gateway: http://localhost:8080/healthz
   - Console: http://localhost:3000/healthz
4. Open the console at http://localhost:3000 to walk through the setup wizard.
5. Stop containers with `docker compose -f docker-compose.quickstart.yml down`.

## Tips

- If you override `AION_DB_*`, also update `DATABASE_URL` so the control plane connects to the correct Postgres instance.
- Use `docker compose logs -f control` and `docker compose logs -f gateway` for troubleshooting.
- Replace placeholder secrets (`AION_GATEWAY_ADMIN_TOKEN`, `AION_GATEWAY_API_KEYS`, `NEXTAUTH_SECRET`) before exposing the stack beyond local development.
