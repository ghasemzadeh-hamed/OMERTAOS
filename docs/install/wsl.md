# WSL installation

AION-OS supports Windows developers through WSL2. Disk actions are skipped; the wizard focuses on profile rendering and service launchers.

## Prerequisites

- Windows 11 with WSL2 enabled (`wsl --install`)
- Ubuntu distribution installed from the Microsoft Store
- Windows Terminal or PowerShell with administrator rights

## Steps

1. Open PowerShell as administrator and run `wsl --install -d Ubuntu` if WSL is not already provisioned.
2. Launch the Ubuntu shell and install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y git nodejs npm python3
   sudo npm install -g pnpm
   ```
3. Clone the repository inside the WSL filesystem (`/home/<user>/aionos`).
4. From the repo root run `./install.sh wsl` to seed required systemd units.
5. Start the wizard UI with `pnpm dev` inside `console`.
6. Visit `http://localhost:3000/wizard` from Windows; the bridge runs inside WSL on port `3030`.
7. Choose **WSL** mode. Storage and bootloader steps will display read-only previews.
8. Apply a profile to render `.env` and write `/etc/aionos/profile.env`.
9. Start services with `./scripts/dev-up.sh` or enable the provided systemd units.
10. Check logs via `journalctl -u aionos-firstboot` to confirm updates and driver checks.

## Limitations

- GPU passthrough depends on the WSL host capabilities; driver installation commands are skipped automatically.
- Secure Boot and disk encryption are not available inside WSL.
- Snapd is disabled by default inside WSL; the security task logs a warning and continues.
