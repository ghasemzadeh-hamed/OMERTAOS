# Native Linux installation

Run the installer on an existing Ubuntu host to reuse the wizard and bridge stack without booting from ISO.

## Requirements

- Ubuntu 22.04 LTS with sudo access
- Internet connectivity for package downloads (or an internal mirror)
- Root privileges to run disk operations

## Steps

1. Clone the repository and install prerequisites:
   ```bash
   sudo apt-get update
   sudo apt-get install -y git nodejs npm python3 make
   ```
2. Install PNPM and dependencies:
   ```bash
   sudo npm install -g pnpm
   cd core/installer/bridge && pnpm install
   ```
3. Export `AIONOS_ALLOW_INSTALL=1` and start the bridge:
   ```bash
   sudo AIONOS_ALLOW_INSTALL=1 pnpm start
   ```
4. In another terminal, start the wizard UI:
   ```bash
   cd console
   pnpm install
   pnpm dev
   ```
5. Browse to `https://localhost:3000/wizard`, accept the certificate warning, and select **Native** mode.
6. Probe hardware, review the storage plan, and confirm profile selection.
7. Apply disk changes only after double-checking the plan output.
8. Watch driver and security task progress under `/var/log/aionos-installer.log`.
9. When the wizard reports success, stop the services and reboot the host.

## Notes

- The bridge enforces root privileges for driver and security tasks.
- Disk apply is rejected unless `AIONOS_ALLOW_INSTALL=1` and mode is `native` or `image`.
- To reuse the rendered `.env`, copy it to `/etc/aionos/profile.env` for first-boot services.
