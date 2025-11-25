# Native services and smoke tests

This repository ships three native systemd units that the GitHub Actions `native` job installs via `scripts/install_linux.sh`:

| Service | Working directory | Entrypoint | Port | Health endpoints | Logs |
| --- | --- | --- | --- | --- | --- |
| `omerta-control.service` | `/opt/omerta/OMERTAOS` | `uvicorn os.control.main:app --host 0.0.0.0 --port 8000 --workers 2` | 8000 | `/health`, `/healthz` | `journalctl -u omerta-control` |
| `omerta-gateway.service` | `/opt/omerta/OMERTAOS/gateway` | `node /opt/omerta/OMERTAOS/gateway/dist/server.js` | 3000 | `/health`, `/healthz` | `journalctl -u omerta-gateway` |
| `omerta-console.service` | `/opt/omerta/OMERTAOS/console` | `node node_modules/next/dist/bin/next start --hostname 0.0.0.0 --port $CONSOLE_PORT` | 3001 (native) | `/health`, `/healthz` (no middleware) | `journalctl -u omerta-console`, `/var/log/omerta-console.log` |

## Installer defaults

`scripts/install_linux.sh` seeds `/opt/omerta/OMERTAOS/.env` with native-friendly defaults:

- Ports are pinned to `CONTROL_PORT=8000`, `GATEWAY_PORT=3000`, `CONSOLE_PORT=3001`.
- `NEXTAUTH_URL` and `AION_CONSOLE_HEALTH_URL` point at the native console (`http://localhost:3001`).
- Control and gateway public URLs default to the native ports so the console renders without extra configuration.

During installation the script now also:

- Applies Prisma migrations for the console against the configured `DATABASE_URL`.
- Seeds a default console admin account (`admin@localhost` / password `admin`). Set `SKIP_CONSOLE_SEED=true` to skip seeding.

## Smoke tests

`scripts/smoke.sh` drives the native health checks used by CI:

1. Waits for systemd to report `omerta-control` and `omerta-gateway` active (best-effort).
2. Polls control and gateway health endpoints, then polls the console at `http://localhost:3001/health`.
3. If any check fails, the script now prints systemd status and the last 50 log lines for the affected unit (plus a longer dump for control).

For Docker Compose based CI runs, `scripts/smoke_e2e.sh` keeps using the container ports (control `8000`, gateway `8080`, console `3000`) and their `/healthz` endpoints.
