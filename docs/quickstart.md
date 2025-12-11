# Quick start

This guide keeps each deployment path concise and aligned with the current compose and installer scripts.

## Containerized quick start

### Linux (Docker Engine)

1. Install Git, Docker Engine 24+ with the Compose plugin, and Python 3.11 or newer.
2. Clone the repository: `git clone https://github.com/Hamedghz/OMERTAOS.git && cd OMERTAOS`.
3. Run `./quick-install.sh` to copy `dev.env` to `.env`, generate development TLS/JWT keys under `config/certs/dev` and `config/keys`, and start [`docker-compose.quickstart.yml`](../docker-compose.quickstart.yml).
4. Wait for services to become healthy:
   - Control API: http://localhost:8000/healthz
   - Gateway: http://localhost:8080/healthz
   - Console: http://localhost:3000/healthz
5. Sign in to the console at http://localhost:3000. Rotate tokens such as `AION_GATEWAY_ADMIN_TOKEN` before exposing the stack outside development.
6. Stop the stack with `docker compose -f docker-compose.quickstart.yml down` when finished.

### Windows 11 / WSL2

1. Install Git for Windows and Docker Desktop with WSL2 integration enabled.
2. Clone the repository: `git clone https://github.com/Hamedghz/OMERTAOS.git` and `cd OMERTAOS`.
3. From an elevated PowerShell prompt, run `.\quick-install.ps1` to copy `dev.env`, generate development certificates, and start [`docker-compose.quickstart.yml`](../docker-compose.quickstart.yml).
4. Open the services once they report healthy:
   - Console: http://localhost:3000
   - Gateway: http://localhost:8080/healthz
   - Control: http://localhost:8000/healthz
5. Stop the environment with `docker compose -f docker-compose.quickstart.yml down`.

## ISO / Kiosk

UNVERIFIED: ISO media and kiosk workflows depend on release artifacts not present in this repository. Follow [`docs/release.md`](release.md) for artifact handling and verify checksums before installation.

## Native Linux

1. Start from Ubuntu 22.04 with sudo access and install prerequisites:
   ```bash
   sudo apt-get update
   sudo apt-get install -y git curl build-essential python3.11 python3.11-venv python3.11-dev nodejs npm
   sudo npm install -g pnpm
   ```
2. Clone the repository and copy `.env` from `.env.example`.
3. Prepare the installer bridge:
   ```bash
   cd core/installer/bridge
   pnpm install
   sudo AIONOS_ALLOW_INSTALL=1 pnpm start
   ```
4. In another terminal, start the console wizard:
   ```bash
   cd console
   pnpm install
   pnpm dev
   ```
5. Browse to https://localhost:3000/wizard, accept the development certificate warning, and select **Native Install**.
6. Confirm profile selection and disk actions only after reviewing the plan. Destructive steps require `AIONOS_ALLOW_INSTALL=1`.
7. Stop services and reboot when the wizard reports success.

## Windows services without Docker

UNVERIFIED: The native Windows service flow referenced by `scripts/install_win.ps1` is legacy and may not match current compose defaults. Prefer the Docker quickstart unless you have validated the Windows service installer in your environment.

## Docker (manual)

1. Ensure Docker Engine 24+ and Docker Compose V2 are installed.
2. Copy `dev.env` to `.env` and adjust credentials only if necessary (default Postgres: `aionos` / `password` / `omerta_db`).
3. Start the stack explicitly:
   ```bash
   docker compose -f docker-compose.quickstart.yml up -d
   ```
4. Access the console at http://localhost:3000 and confirm gateway health at http://localhost:8080/healthz.
5. Tear down with `docker compose -f docker-compose.quickstart.yml down`.
