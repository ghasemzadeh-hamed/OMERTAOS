# Native Installation Guide

This document describes how to install and operate **OMERTAOS/AION-OS** without Docker. It covers
Linux (Ubuntu/Debian) and Windows 11 environments and explains how to run the system as managed
services.

> **Note**
> The container-first installation flow is now provided by `scripts/quicksetup.sh` and
> `scripts/quicksetup.ps1`. The native installers described below are considered legacy and are kept
> for operators that require systemd/NSSM deployments.

- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [Linux installation](#linux-installation)
- [Windows installation](#windows-installation)
- [Post-install checks](#post-install-checks)
- [Managing services](#managing-services)
- [Reverse proxy (Apache)](#reverse-proxy-apache)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Common

- Internet access for package downloads and GitHub cloning.
- Access to a PostgreSQL server (local installation is automated).
- Redis server (installed locally by the Linux script; install manually on Windows).

### Linux (Ubuntu / Debian)

The `scripts/install_linux.sh` script installs the following packages if they are missing:

- `git`, `curl`, `ca-certificates`
- Build toolchain: `build-essential`, `python3.11`, `python3.11-venv`, `python3.11-dev`
- `redis-server`, `postgresql`, `postgresql-contrib`
- Node.js 18 LTS (via NodeSource if the distro version is older)

You need sudo access to install packages and create systemd units.

### Windows 11

Ensure the following tools are installed before running the PowerShell installer:

- Git for Windows
- Python 3.11 (available in `PATH` as `python`)
- Node.js 18 LTS
- PostgreSQL (local or remote) and Redis (optional but recommended locally)
- [NSSM](https://nssm.cc/) installed at `C:\nssm\nssm.exe` or export `NSSM_PATH`
- PowerShell 7+ is recommended (Windows PowerShell 5.1 also works)

## Quick start

### Linux one-liner

```bash
curl -fsSL https://raw.githubusercontent.com/Hamedghz/OMERTAOS/main/scripts/install_linux.sh | bash
```

> Set `APP_ROOT`, `REPO`, `DB_USER`, `DB_PASS`, or other environment variables before executing to
> customize the installation.

### Windows

Open **PowerShell as Administrator**, clone the repository, and run:

```powershell
Set-Location C:\path\to\OMERTAOS
.\scripts\install_win.ps1
```

You can override defaults with environment variables:

```powershell
$env:APP_ROOT = 'D:\Omerta'
$env:DB_PASS = 'SuperSecret123!'
.\scripts\install_win.ps1
```

## Linux installation

1. Review `config/templates/.env.example` and set any desired environment overrides (ports, database name, secrets).
2. Run `scripts/install_linux.sh` (or use the curl one-liner shown above). The script performs:
   - Package installation via `apt`.
   - Creation of the `omerta` service account and checkout of the repository into `/opt/omerta/OMERTAOS` (override with `APP_ROOT`).
   - Python virtual environment creation and dependency installation for the control plane.
   - Node.js dependency installation and builds for the console and gateway using `pnpm`.
   - PostgreSQL database/user provisioning (idempotent) and `.env` updates.
   - Symlinks for `.env` in `gateway/` and `console/` for build/runtime parity.
   - Deployment of systemd units (`omerta-control`, `omerta-gateway`, `omerta-console`) and immediate start.

Environment variables accepted by the script:

- `APP_ROOT` - installation prefix (default `/opt/omerta`).
- `APP_USER` - service user (default `omerta`).
- `DB_USER`, `DB_PASS`, `DB_NAME` - override database credentials.
- `REPO` - alternative Git repository URL.

The script is idempotent - rerunning will pull updates, reinstall dependencies as needed, and restart
services.

## Windows installation

1. Ensure prerequisites are installed and available in `PATH`.
2. From an elevated PowerShell session inside the repository, run `scripts/install_win.ps1`.
   - Running from within an existing clone will reuse that checkout instead of creating a fresh copy (pending an installer logic fix).
   - Setting `APP_ROOT` keeps the legacy behavior that clones the repository under that directory, which is useful when staging multiple service installs side by side.
3. The script will:
   - Clone or update the repository into `C:\Omerta\OMERTAOS` (override with `APP_ROOT`).
   - Create/update a Python virtual environment and install control-plane dependencies.
   - Install `pnpm` globally (if missing), then install/build the console and gateway.
   - Copy `config/templates/.env.example` to `.env` (first run) and keep gateway/console copies in sync.
   - Provision PostgreSQL objects when `psql` is available (warnings are printed if skipped).
   - Register three Windows Services using NSSM: `OmertaControl`, `OmertaGateway`, `OmertaConsole`.
   - Start all services automatically.

Useful environment variables:

- `APP_ROOT`, `REPO`, `DB_USER`, `DB_PASS`, `DB_NAME` - behave like the Linux installer.
- `NSSM_PATH` - path to `nssm.exe` if not using the default `C:\nssm\nssm.exe`.

## Post-install checks

After either installer completes:

- Verify ports:
  - Control API: <http://localhost:8000/health>
  - Gateway API: <http://localhost:3000/health>
  - Console UI: <http://localhost:3001/>
- Run the smoke tests:
  - Linux: `./scripts/smoke.sh`
  - Windows: `.\scripts\smoke.ps1`

The smoke scripts accept `CONTROL_HEALTH_URL`, `GATEWAY_HEALTH_URL`, `CONSOLE_HEALTH_URL`, and
`SKIP_CONSOLE_HEALTH=true` to target alternate hosts or skip UI validation.

## Managing services

### Linux systemd units

The installer deploys service files under `/etc/systemd/system/`:

- `omerta-control.service`
- `omerta-gateway.service`
- `omerta-console.service`

Use the provided Makefile shortcuts (requires sudo for most operations):

```bash
make status    # Show systemd status
make logs      # Tail recent journal entries
make restart   # Restart all services
make stop      # Stop services
make start     # Start services
```

### Windows services

Services installed via NSSM:

- `OmertaControl`
- `OmertaGateway`
- `OmertaConsole`

Manage them with the Services MMC snap-in or PowerShell:

```powershell
Get-Service Omerta*
Restart-Service OmertaGateway
```

## Reverse proxy (Apache)

A sample Apache configuration is available at `configs/apache/omerta.conf`. It proxies HTTP and
WebSocket traffic to the gateway service on port 3000. Enable required Apache modules (`proxy`,
`proxy_http`, `proxy_wstunnel`, `rewrite`) and copy the file to `/etc/apache2/sites-available/` (or
the Windows Apache equivalent). Enable TLS termination as needed for production deployments.

## Troubleshooting

- **Port conflicts**: Adjust `GATEWAY_PORT`, `CONTROL_PORT`, or `CONSOLE_PORT` in `.env` before running
  the installers. Rerun the installer to propagate changes to services.
- **Database authentication failures**: Ensure PostgreSQL trusts local connections or update
  credentials in `.env` and rerun the installer.
- **pnpm not found in services**: The systemd units set `PATH` explicitly. If you relocate pnpm,
  update the unit files under `configs/systemd/` and rerun the installer.
- **Windows services fail immediately**: Check the NSSM logs in `C:\ProgramData\NSSM\service\<Name>`
  and ensure Redis/PostgreSQL endpoints are reachable.

For additional automation (backups, TLS termination, monitoring), adapt the scripts and unit files in
`configs/` to your environment.
