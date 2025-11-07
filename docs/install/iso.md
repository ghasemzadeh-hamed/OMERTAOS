# ISO / Kiosk installation

The kiosk ISO delivers a locked-down Chromium session that hosts the Next.js installer wizard. Disk operations are gated behind `AIONOS_ALLOW_INSTALL=1` to prevent accidental wipes.

## Prerequisites

- Ubuntu 22.04 or later build host
- `make`, `xorriso`, `squashfs-tools`, and `docker` for image assembly
- Access to the release signing keys if you intend to publish the ISO

## Build steps

1. Run `make iso` from the repository root. This stages kernel modules, the kiosk systemd units, and the Next.js wizard build.
2. The build populates `core/iso/out/` with the ISO image and checksum manifest.
3. To update the offline cache, place debs under `core/iso/cache/` before running `make iso`.
4. Sign the final ISO with `cosign sign-blob` if desired, then upload to your release channel.

## Boot flow

1. Boot the target system from USB.
2. The kiosk session auto-launches Chromium pointing to `https://localhost/wizard`.
3. Confirm networking; the wizard relies on the local bridge (`core/installer/bridge/server.ts`).
4. Set locale, mode, and storage preferences. Secure Boot and full-disk encryption toggles live on the storage step.
5. When prompted to apply disk changes, press the gate icon, export `AIONOS_ALLOW_INSTALL=1`, and re-run the apply action.
6. Monitor `/var/log/aionos-installer.log` for driver and security task output.
7. Reboot when the wizard reports success.

## Offline mode

- Toggle the offline cache switch in the wizard to rely solely on `core/iso/cache/` packages.
- Ensure GPU drivers (NVIDIA, AMD, Intel), firmware bundles, and critical security updates are mirrored into the cache.
