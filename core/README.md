# AION-OS Core Builder

This directory contains the tooling required to produce a bare-metal, bootable AION-OS installer ISO that provisions the OMERTAOS stack on commodity hardware.

## Layout

- `iso/` – Scripts and resources for generating the live ISO image.
  - `build.sh` – Main entrypoint; bootstraps an Ubuntu Jammy rootfs, installs Calamares, copies the repository, and emits a hybrid BIOS/UEFI ISO.
  - `chroot-setup.sh` – Optional helper script for additional chroot provisioning steps.
  - `includes/` – Placeholder directory for custom hooks or static assets bundled into the ISO filesystem.
- `installer-ui/` – Calamares configuration, module definitions, and branding for the graphical installer.
- `firstboot/` – Systemd unit and script that finalise the installation on first boot (driver detection, dependency setup, enabling services).
- `systemd/` – Units that launch the OMERTAOS gateway, control plane, and console as part of the `aionos.target` stack.

## Building an ISO

```bash
cd core/iso
./build.sh
```

The resulting `aionos-installer.iso` will be placed in the repository root. Ensure the required host dependencies listed at the top of `build.sh` are installed before running the script.
