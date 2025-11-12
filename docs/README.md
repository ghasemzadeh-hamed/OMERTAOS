# AION-OS Documentation Hub

This directory provides enterprise-ready runbooks, covering installation, configuration, and operations for every deployment mode.

## Quick start

Use [`quickstart.md`](quickstart.md) for a guided ten-step launch path across ISO, native Linux, WSL, and Docker modes.

## Installation guides

Mode-specific instructions live under [`install/`](install):

- [`install/iso.md`](install/iso.md) - build and boot the kiosk ISO, including offline cache support.
- [`install/enterprise_iso_profile.md`](install/enterprise_iso_profile.md) - preconfigure the kiosk ISO for the enterprise profile and SEAL memory stack.
- [`install/native.md`](install/native.md) - run the installer bridge on an existing Ubuntu host.
- [`install/wsl.md`](install/wsl.md) - bring the stack to Windows via WSL without touching disks.
- [`install/docker.md`](install/docker.md) - compose services for local or CI-driven clusters.

## Profiles and automation

Profile behaviour, feature toggles, and service enablement are described in [`profiles/`](profiles):

- [`profiles/user.md`](profiles/user.md)
- [`profiles/pro.md`](profiles/pro.md)
- [`profiles/enterprise.md`](profiles/enterprise.md)

The installer schema lives in `core/installer/profile/schemas.ts`, and default YAML manifests sit in `core/installer/profile/defaults/`.

## Security and compliance

Baseline hardening, update cadence, and secure boot guidance are documented in [`security/`](security):

- [`security/baseline.md`](security/baseline.md)
- [`security/updates.md`](security/updates.md)
- [`security/secure-boot-fde.md`](security/secure-boot-fde.md)

## Hardware compatibility

GPU, NIC, Wi-Fi, and firmware matrices live in [`hcl/`](hcl). Use [`hcl/index.md`](hcl/index.md) as the entry point, with detail pages for GPUs (`hcl/gpu.md`) and networking (`hcl/nic.md`).

## Operations

- [`troubleshooting.md`](troubleshooting.md) - quick fixes for the most common install and runtime issues.
- [`release.md`](release.md) - SBOM, signing, and release validation process.
- [`privacy.md`](privacy.md) - optional telemetry and data handling.
