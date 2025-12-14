# Windows Setup for OMERTAOS

This guide aligns the Windows experience with the Linux quicksetup while preserving the container topology (Control, Gateway, Console).

## Prerequisites
- Windows 10/11 with administrator rights for Docker Desktop.
- Docker Desktop with Compose v2 enabled and running.
- Git.
- PowerShell 7+ (WSL2 optional for shell only).

## Quick setup
Run from the repository root in PowerShell:

```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\quicksetup.ps1
```

What the script does:
- Creates `.env` from the repo templates if it does not already exist and preserves existing values.
- Writes profile metadata to `.aionos/profile.json`.
- Starts the Control (8000), Gateway (3000), and Console (3001) containers with `docker compose up -d --build`.
- Prints generated admin tokens and credentials.

Flags (optional):
- `-NonInteractive` to skip prompts and auto-generate secrets.
- `-ComposeFile <path>` to target an alternate compose file (defaults to `docker-compose.yml`).

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

## Health checks
Default endpoints (override with `CONTROL_HEALTH_URL`, `GATEWAY_HEALTH_URL`, or `CONSOLE_HEALTH_URL` if needed):
```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/healthz | Out-Null
Invoke-WebRequest -UseBasicParsing http://localhost:3000/health | Out-Null
Invoke-WebRequest -UseBasicParsing http://localhost:3001/health | Out-Null
```

## Smoke test
```powershell
PowerShell -ExecutionPolicy Bypass -File .\scripts\smoke_windows.ps1
```
The script runs `docker compose up` (respecting `-ComposeFile` and `-NoBuild` flags), waits for Control, Gateway, and Console to report healthy, and prints diagnostics on failure.

## Troubleshooting
- Ensure Docker Desktop is running: `docker info` should return a server version.
- If Compose v2 is missing, install or enable it in Docker Desktop; the scripts warn when falling back to `docker-compose`.
- Ports 8000 (Control), 3000 (Gateway), and 3001 (Console) must be free.
