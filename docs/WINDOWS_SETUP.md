# Windows Setup for OMERTAOS

This guide aligns the Windows experience with the Linux quicksetup while preserving the container topology (Control, Gateway, Console).

## Prerequisites
- Windows 10/11 with administrator rights for Docker Desktop.
- PowerShell 5.1 **or** PowerShell 7+.
- Docker Desktop with Compose v2 enabled **and running** (WSL integration recommended).
- Git.
- Optional: WSL2 for shell convenience.

Make sure Docker is reachable and Compose v2 is available:

```powershell
docker info
docker compose version
```

Validate your environment before running QuickSetup:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\selfcheck_windows.ps1
```

## Quick setup
Run from the repository root in PowerShell:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\quicksetup.ps1
```

Add `-SkipSelfCheck` if you already ran `selfcheck_windows.ps1` in the same session.

The quicksetup script now:
- Detects Docker Compose v2 (falls back to `docker-compose` when necessary) without relying on "docker compose" parsing quirks.
- Uses the `windows` Compose profile automatically on Windows/WSL to relax startup gating while keeping other profiles (for example, `vault`) intact.
- Persists Qdrant data in a named volume for stability.
- Writes defaults for ORCH_* and CODER_* variables to `.env` to silence warning messages.
- Starts the stack with `docker compose -f docker-compose.yml --profile windows up -d --remove-orphans`, then **waits up to three minutes for services that report `health: starting`** before failing.
- Treats `health: starting` as expected during boot and only errors on `unhealthy`/`exited` states; on timeout it prints `compose ps` and the last 200 log lines automatically.
- Opens the Console login page in your default browser once the endpoint answers (200/302) and prints the URLs and credentials on completion.
- Publishes the Console UI on `http://localhost:3000` while keeping Gateway at `http://localhost:8080` and Control at `http://localhost:8000`.

What the script does:
- Creates `.env` from the repo templates if it does not already exist and preserves existing values.
- Writes profile metadata to `.aion/profile.json`.
- Detects Compose deterministically (docker compose v2 preferred, docker-compose fallback) and shows the exact command it runs.
- Starts the Control (8000), Gateway (8080), and Console (3000) containers with compose and surfaces stderr on failure.
- Prints generated admin tokens and credentials.

Flags (optional):
- `-NonInteractive` to skip prompts and auto-generate secrets.
- `-ComposeFile <path>` to target an alternate compose file (defaults to `docker-compose.yml`).
- `-SkipSelfCheck` to skip the preflight validations when chaining runs.

## Start, stop, and logs
```powershell
# Start or restart
PowerShell -ExecutionPolicy Bypass -File .\scripts\quicksetup.ps1

# Stop
$composeFile = 'docker-compose.yml'
docker compose -f $composeFile down

# Logs
$composeFile = 'docker-compose.yml'
docker compose -f $composeFile logs -f --tail 200

# Status
docker compose -f $composeFile ps
```

If you run with an additional profile (for example `vault`), add it consistently:

```powershell
docker compose -f $composeFile --profile windows --profile vault up -d --remove-orphans
docker compose -f $composeFile --profile windows --profile vault ps
```

## Health checks
Default endpoints (override with `CONTROL_HEALTH_URL`, `GATEWAY_HEALTH_URL`, or `CONSOLE_HEALTH_URL` if needed):
```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/healthz | Out-Null
Invoke-WebRequest -UseBasicParsing http://localhost:3000/health | Out-Null
Invoke-WebRequest -UseBasicParsing http://localhost:3001/ | Out-Null
```

The Control API now serves both `/healthz` and `/api/healthz` for backward compatibility so internal callers no longer hit a 404.

## Quick Windows smoke test
1. `docker compose -f docker-compose.yml down -v`
2. `pwsh ./install.ps1` (or `PowerShell -ExecutionPolicy Bypass -File .\install.ps1`)
3. Wait for the readiness loop to report success, confirm `docker compose -f docker-compose.yml ps` shows `running` (health `starting` is acceptable while bootstrapping), and verify your browser opens `http://localhost:3001/login` automatically.

## Smoke test
```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\smoke_windows.ps1
```
The script runs `docker compose up` (respecting `-ComposeFile` and `-NoBuild` flags), waits for Control, Gateway, and Console to report healthy, and prints diagnostics on failure.

## Troubleshooting
- Ensure Docker Desktop is running: `docker info` should return a server version.
- If Compose v2 is missing, install or enable it in Docker Desktop; the scripts warn when falling back to `docker-compose`.
- Ports 8000 (Control), 3000 (Gateway), and 3001 (Console) must be free.
- If you see `Docker daemon not reachable. Ensure Docker Desktop is running and WSL integration is enabled.`, start Docker Desktop and re-run `scripts/selfcheck_windows.ps1` to confirm connectivity.
- If compose retries fail, the script prints the exact command and the first lines of stderr—no need to dig through hidden logs.
- For `qdrant` unhealthy or startup stalls, the Windows profile relaxes gating to `service_started` and the data directory is now stored in a named volume (`qdrant-data`). You can inspect with `docker compose -f docker-compose.yml --profile windows ps` and `docker compose -f docker-compose.yml --profile windows logs --tail=200`.
- The installer will open the Console URL automatically after the services become reachable. If the browser does not open, manually visit `http://localhost:3001/` and use the printed admin credentials.
