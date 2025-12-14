# Windows Setup Parity Report

## Step 0 - Install entry points
- scripts/quicksetup.sh: Linux container quickstart for Control/Gateway/Console via docker compose.
- scripts/quicksetup.ps1: Windows PowerShell quickstart for the same compose stack.
- scripts/smoke.sh: Linux smoke/health verification for running services.
- scripts/smoke.ps1: Legacy Windows health probe for manual/native installs.
- scripts/smoke_windows.ps1: Windows compose smoke test (added for parity).
- install.sh / install.ps1: wrappers that call the quicksetup scripts.
- docker-compose.yml: canonical compose stack with Control, Gateway, Console, and dependencies.
- docker-compose.quickstart.yml: simplified compose intended for minimal/local runs.
- docker-compose.local.yml and docker-compose.obsv.yml: optional compose overlays/profiles.
- .github/workflows/*.yml: CI workflows (Linux runners only; no Windows workflow present).

## Step 1 - Canonical settings (source of truth)
- Services and ports (docker-compose.yml): Control HTTP 8000 and gRPC 50051; Gateway 3000; Console 3001. Dependencies: Postgres 5432, Redis 6379, Qdrant 6333, MinIO 9000/9001.
- Health expectations: Control healthcheck is served by the Control container process (smoke scripts target `/healthz`); Gateway health is `/health`; Console health is `/health` (compose healthcheck uses `/healthz`).
- Environment defaults (dev.env + compose): `AION_CONTROL_BASE_URL` http://control:8000, `AION_CONTROL_GRPC` http://control:50051, `AION_GATEWAY_PORT` 3000, `CONSOLE_PORT` 3001, `NEXT_PUBLIC_GATEWAY_URL` http://gateway:3000 inside containers, and public defaults of `CONTROL_BASE_URL=http://localhost:8000`, `GATEWAY_BASE_URL=http://localhost:3000`, `CONSOLE_BASE_URL=http://localhost:3001`.
- Console to Gateway routing: Console uses `NEXT_PUBLIC_GATEWAY_URL` (default http://gateway:3000) and admin token variables; Gateway reaches Control via `AION_CONTROL_BASE_URL` and `AION_CONTROL_GRPC` (default http://control:8000 and http://control:50051).

## Step 2 - Baseline Linux flow
- Prerequisites: git, docker with compose v2, python3, curl/wget enforced by scripts/quicksetup.sh.
- Path handling: uses the repository root as working directory; ensures `.env` from templates and writes profile metadata.
- Bring-up: `docker compose -f docker-compose.yml up -d --build` from scripts/quicksetup.sh.
- Health checks: scripts/smoke.sh polls `http://localhost:8000/healthz`, `http://localhost:3000/health`, and `http://localhost:3001/health` with retries and diagnostics.
- Logs: `docker compose logs -f --tail=200` recommended from Linux quickstart summary.

## Step 3 - Windows parity check (issues observed)
- Blocker: No compose-based smoke test for Windows to mirror Linux health checks.
- Major: quicksetup.ps1 could clone into `OMERTAOS/OMERTAOS` when run from an archive without `.git`, creating nested repos and unexpected working directories.
- Major: No preflight check to ensure Docker Desktop engine was running before compose, leading to confusing failures.
- Minor: Mixed compose invocation (`docker compose` vs `docker-compose`) without a clear preference for v2.
- Minor: Logged NEXTAUTH_URL pointed to port 3000 instead of the Console default port 3001.

## Step 4 - Parity matrix
| Aspect | Linux | Windows (updated) | Parity |
| --- | --- | --- | --- |
| Prerequisites | git, docker+compose v2, python3, curl/wget enforced in quicksetup.sh | git, docker+compose v2 checked; Docker engine availability verified; curl/wget required | ✔ |
| Working directory | Uses repo root; no cloning if already in place | Uses repo root from script location; skips cloning when compose layout exists | ✔ |
| Env handling | `.env` created from templates; preserves existing keys | Same behavior; no overwrite when `.env` exists | ✔ |
| Ports & services | Control 8000/50051, Gateway 3000, Console 3001 | Same compose defaults and logging | ✔ |
| Start/stop | `docker compose -f docker-compose.yml up -d --build` / `down` | Same commands via quicksetup.ps1 and smoke_windows.ps1 | ✔ |
| Health checks | smoke.sh polls /healthz (Control) and /health (Gateway/Console) | smoke_windows.ps1 polls the same endpoints with retries and diagnostics | ✔ |
| Dashboard access | Console at http://localhost:3001 via Gateway at http://localhost:3000 | Same URLs documented and logged | ✔ |

## Step 5 - Fixes applied (file-by-file)
- scripts/quicksetup.ps1: added Docker Desktop preflight, consistent compose command resolution, correct working-directory resolution to avoid nested clones, refreshed path handling, and corrected NEXTAUTH_URL log output.
- scripts/smoke_windows.ps1: new compose-based smoke test aligned with Linux endpoints and diagnostics.
- docs/WINDOWS_SETUP.md: refreshed Windows quickstart, commands, health checks, and troubleshooting.
- docs/WINDOWS_SETUP_PARITY_REPORT.md: documented parity findings and resolutions.

## Remaining limitations
- Windows automation still depends on Docker Desktop being started manually before running the scripts.
- No Windows CI workflow exists; Windows verification remains a manual/local step.
