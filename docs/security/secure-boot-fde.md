# Secure Boot and full-disk encryption

AION-OS exposes Secure Boot and full-disk encryption toggles during the storage step of the wizard. Disk operations remain gated by `AIONOS_ALLOW_INSTALL=1`.

## Secure Boot

1. Ensure firmware Secure Boot is enabled before launching the installer.
2. The ISO ships with shim and grub signed by Canonical; local builds require signing with your keys.
3. When installing drivers that use DKMS, the wizard will prompt for MOK enrolment on reboot.
4. Document key handling procedures in your compliance repository.

## Full-disk encryption

1. Select the encryption checkbox on the storage step; the installer creates a LUKS volume for root.
2. Recovery keys are written to `/root/aionos-recovery.txt`; store them in Vault or a secure secret manager.
3. TPM unlock support is on the roadmap; for now, manual passphrases are required at boot.

## Verification

- Use `mokutil --sb-state` after install to confirm Secure Boot state.
- Run `cryptsetup status /dev/mapper/aionos-root` to confirm LUKS activation.
- Keep `/var/log/aionos-installer.log` and `/var/log/aionos-firstboot.log` for audit purposes.
