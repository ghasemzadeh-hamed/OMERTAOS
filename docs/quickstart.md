# Quick start

This guide condenses each supported deployment into ten steps or fewer. Run every command as root or with `sudo` unless noted.

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
2. Clone the repository and install dependencies (`apt-get install -y nodejs npm git`).
3. Run `pnpm install` inside `core/installer/bridge`.
4. Launch the bridge (`AIONOS_ALLOW_INSTALL=1 pnpm start`).
5. Start the wizard UI (`pnpm dev` inside `console`).
6. Connect to `https://localhost:3000/wizard` and select **Native Install**.
7. Pick your profile and network options.
8. Confirm disk operations only after reviewing the plan.
9. Wait for the security and driver tasks to complete.
10. Reboot when prompted.

## Windows / WSL

1. Enable WSL2 and install Ubuntu from the Microsoft Store.
2. Inside the Ubuntu shell, clone the repository and run `sudo ./scripts/quicksetup.sh --profile professional --local`.
3. Launch the wizard (`pnpm dev` in `console`) and open it in Windows Edge/Chrome.
4. Select **WSL** mode in the wizard; storage options will be disabled automatically.
5. Apply a profile to render `.env` and configure services.
6. Run `./scripts/dev-up.sh` to start core services in the WSL distro.
7. Use `aionos-firstboot` service logs to verify updates (`journalctl -u aionos-firstboot`).
8. Launch the console UI from Windows (`http://localhost:3000`).

## Docker

1. Ensure Docker Engine 24+ and Docker Compose V2 are installed.
2. Clone the repository and copy `.env` from `config/templates/.env.example`.
3. Set `AION_PROFILE` to `user`, `pro`, or `enterprise` in `.env`.
4. Run `docker compose up --profile base -d` (add `pro` or `enterprise` profiles as needed).
5. Access the wizard at `http://localhost:3000/wizard` to review status.
6. Trigger driver and security tasks from the wizard if desired (they run as no-ops in containers).
7. Confirm service health via the console dashboard.
8. Tear down with `docker compose down` when finished.
