# Quick start

This guide condenses each supported deployment into ten steps or fewer. Run every command as root or with `sudo` unless noted.

## Containerized quick start

### Linux (Docker Engine)

1. Install Git, Docker Engine 24+ with the Compose plugin, and Python 3.11 or newer.
2. Clone the repository: `git clone https://github.com/ghasemzadeh-hamed/OMERTAOS.git && cd OMERTAOS`.
3. Execute the wrapper: `./install.sh --profile user` (substitute `professional` or `enterprise-vip` as needed).
4. Add `--local` to target [`docker-compose.local.yml`](../docker-compose.local.yml) for lightweight developer profiles.
5. Use `--update` when you want the script to fetch the latest commits before launching services.
6. Monitor the provisioning logs streamed by [`scripts/quicksetup.sh`](../scripts/quicksetup.sh) for preflight checks and container startup.
7. Open the console at `http://localhost:3000` and complete the onboarding wizard.
8. Verify service health from the dashboard (`Control`, `Gateway`, `Console` tiles should show green).
9. When finished, run `docker compose down` to stop the stack.

### Windows 11 / WSL2

1. Install Git for Windows, Docker Desktop (WSL integration enabled), and PowerShell 7+.
2. Clone the repository: `git clone https://github.com/ghasemzadeh-hamed/OMERTAOS.git`.
3. From an elevated PowerShell prompt in the repository root, run `pwsh ./install.ps1 -Profile user` (or `professional` / `enterprise-vip`).
4. Append `-Local` for the developer overlay or `-Update` to pull fresh commits before launching containers.
5. The script orchestrates [`docker-compose.yml`](../docker-compose.yml) via [`scripts/quicksetup.ps1`](../scripts/quicksetup.ps1); watch the output for prerequisite warnings.
6. When prompted, sign in to Docker Desktop so the compose project can start.
7. Open `http://localhost:3000` from Windows to finish the wizard.
8. Stop the environment with `docker compose down` (PowerShell) when you are done testing.

## ISO / Kiosk

1. Fetch the latest release artifact from the release bucket and verify the checksum (see [`docs/release.md`](release.md)).
2. Write the ISO to a USB drive (`dd if=aionos.iso of=/dev/sdX bs=4M status=progress`).
3. Boot the target system with Secure Boot enabled if supported.
4. When the kiosk launches, confirm networking and press **Start Installer**.
5. Select locale, keyboard, and installation mode (ISO defaults to `native`).
6. Review storage layout; enable full-disk encryption if desired.
7. Export `AIONOS_ALLOW_INSTALL=1` in the console gate and confirm disk actions.
8. Choose a profile (user, pro, enterprise) and review the summary.
9. Trigger the install and monitor `/var/log/aionos-installer.log` for progress.
10. Reboot into the installed system.

## Native Linux

1. Start from an Ubuntu 22.04 base with network access.
2. Install prerequisites: `sudo apt-get install -y git curl build-essential python3.11 python3.11-venv python3.11-dev` and install Node.js 18 LTS plus `pnpm` (`core/installer/bridge` relies on them).
3. Clone the repository and copy `.env` from `config/templates/.env.example`.
4. Run `pnpm install` in `core/installer/bridge` to prepare the privileged task server.
5. Launch the bridge with `AIONOS_ALLOW_INSTALL=1 pnpm start`.
6. In a second terminal, run `pnpm install && pnpm dev` inside `console` to start the wizard UI.
7. Connect to `https://localhost:3000/wizard` and select **Native Install**.
8. Pick your profile and network options.
9. Confirm disk operations only after reviewing the plan.
10. Reboot when prompted.

## Windows services without Docker

1. Install Git for Windows, Python 3.11, Node.js 18 LTS, PostgreSQL, Redis, and NSSM (`C:\\nssm\\nssm.exe` or export `NSSM_PATH`).
2. Clone the repository and inspect `config/templates/.env.example` for port/database overrides.
3. Run `pwsh ./scripts/install_win.ps1` from an elevated PowerShell prompt.
4. When prompted, provide database credentials or allow the script to create them (if PostgreSQL tools are present).
5. Wait for the script to build the console and gateway via `pnpm`, register the `Omerta*` services, and start them.
6. Confirm health at `http://localhost:3000` and tail service logs if troubleshooting is required.

## Docker (manual)

1. Ensure Docker Engine 24+ and Docker Compose V2 are installed.
2. Clone the repository and copy `.env` from `config/templates/.env.example`.
3. Set `AION_PROFILE` to `user`, `professional`, or `enterprise-vip` in `.env`.
4. Run `docker compose up --profile base -d` (add `professional` or `enterprise` profiles as needed).
5. Access the wizard at `http://localhost:3000/wizard` to review status.
6. Trigger driver and security tasks from the wizard if desired (they run as no-ops in containers).
7. Confirm service health via the console dashboard.
8. Tear down with `docker compose down` when finished.
