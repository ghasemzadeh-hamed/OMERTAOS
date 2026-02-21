# CI smoke and health checks

This repository now relies on two primary smoke test flows:

- **Docker-based E2E** (`scripts/smoke_e2e.sh`): runs against the docker-compose stack using the `CONTROL_BASE_URL`, `GATEWAY_BASE_URL`, and `CONSOLE_BASE_URL` variables (defaults: `http://localhost:8000`, `http://localhost:8080`, `http://localhost:3000`). It requires the `/healthz` endpoints on control, gateway, and console to return 200. Admin and UI probes are best-effort and emit warnings only.
- **Native/systemd** (`scripts/smoke.sh`): targets locally installed services with the same base URL defaults. It retries `/healthz` checks and surfaces diagnostics without failing on missing `systemctl` units when run in unsupported environments.

## Running locally

1. Start the docker stack:
   ```sh
   docker compose up -d
   ./scripts/smoke_e2e.sh
   ```
2. For native/systemd installs, ensure services are running on localhost ports (defaults above) and run:
   ```sh
   ./scripts/smoke.sh
   ```

## Environment notes

- Vault integration is optional for quickstart. `VAULT_ENABLED=false` and the defaults in `dev.env` allow compose to start without external secrets.
- Console health endpoints `/health` and `/healthz` are lightweight and should not depend on databases or external services.
- The console seed script creates an admin user with `CONSOLE_ADMIN_EMAIL` and `CONSOLE_ADMIN_PASSWORD` (defaults `admin@local` / `admin123`) unless `SKIP_CONSOLE_SEED` is set to a truthy value.
