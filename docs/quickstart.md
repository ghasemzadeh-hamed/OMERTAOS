# Quick start

This guide keeps each deployment path concise and aligned with the current compose and installer scripts.

## Containerized quick start

### Linux (Docker Engine)

1. Install Git, Docker Engine 24+ with the Compose plugin, and Python 3.11 or newer.
2. Clone the repository: `git clone https://github.com/Hamedghz/OMERTAOS.git && cd OMERTAOS`.
3. Run `./quick-install.sh` to copy `dev.env` to `.env`, generate development TLS/JWT keys under `config/certs/dev` and `config/keys`, and start [`docker-compose.quickstart.yml`](../docker-compose.quickstart.yml). The script pins `DATABASE_URL`, `AION_CONTROL_POSTGRES_DSN`, and the console admin credentials so the console, gateway, and control all share the same Postgres datastore.
4. Wait for services to become healthy:
   - Control API: http://localhost:8000/healthz
   - Gateway: http://localhost:8080/healthz
   - Console: http://localhost:3000/healthz
5. Sign in to the console at http://localhost:3000 using the credentials printed by `quick-install.sh` (email/password/API key). These are the only valid development admin credentials; the console seeds the same values into Postgres on startup. Rotate tokens such as `AION_GATEWAY_ADMIN_TOKEN` before exposing the stack outside development.
6. Run `make doctor` if you need a quick diagnostic: it confirms the console container has `DATABASE_URL`, checks gateway `/v1/config/profile` with the dev API key, verifies control health, and prints which database backend is active.
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

### Dev auth and datastore contract

- Docker/quickstart deployments never fall back to SQLite. `DATABASE_URL` must be set and points to Postgres for both the console and control.
- The console seeds its admin user from `CONSOLE_ADMIN_EMAIL`/`CONSOLE_ADMIN_PASSWORD` (populated by `quick-install.sh` using the printed dev credentials) and uses the same Postgres DSN as the gateway/control services.
- Gateway auth and console auth share the same API key/token bundle (`DEV_API_KEY`, `AION_DEV_ADMIN_TOKEN`, `AION_GATEWAY_API_KEYS`). Keep these values aligned when rotating secrets.
- To reset bootstrap cleanly, stop the stack and remove the Postgres volume (`docker compose -f docker-compose.quickstart.yml down -v`) before rerunning `./quick-install.sh`.

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
