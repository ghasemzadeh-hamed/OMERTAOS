# Native Linux installation

Run the installer on an existing Ubuntu host to reuse the wizard and bridge stack without booting from ISO.

## Requirements

- Ubuntu 22.04 LTS with sudo access
- Internet connectivity for package downloads (or an internal mirror)
- Root privileges to run disk operations

## Steps

1. Install prerequisites:
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
4. Launch the console wizard in a separate terminal:
   ```bash
   cd console
   pnpm install
   pnpm dev
   ```
5. Visit https://localhost:3000/wizard, accept the development certificate warning, and select **Native Install**.
6. Review hardware probes and the storage plan before approving changes. Destructive steps require `AIONOS_ALLOW_INSTALL=1`.
7. After the wizard reports success, stop services and reboot the host.

## Notes

- The bridge enforces root privileges for driver and security tasks.
- Copy the rendered `.env` to `/etc/aionos/profile.env` if you want systemd units to reuse the same configuration on first boot.
