# Troubleshooting

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Wizard cannot reach the bridge

- Confirm the bridge is running (`pnpm start` in `core/installer/bridge`).
- Verify port `3030` is open (`ss -tlnp | grep 3030`).
- For ISO mode, press `Ctrl+Alt+F2` to access the shell and check logs.

## Disk apply blocked

- Ensure you exported `AION_ALLOW_INSTALL=1` in the gate terminal.
- Confirm the install mode is `native` or `image`; WSL and Docker skip disk actions.
- Check `journalctl -u aion-installer` for permission errors.

## Driver installation failed

- Inspect `/var/log/aion-installer.log` for the failed command.
- Re-run the driver task from the wizard or execute `core/firstboot/aion-firstboot.sh` manually.
- Secure Boot users may need to enrol DKMS modules via MOK.

## First-boot service stuck

- Use `journalctl -u aion-firstboot` to track progress.
- Confirm profile variables exist in `/etc/aion/profile.env`.
- Re-run `sudo /usr/lib/aion/aion-firstboot.sh` to resume.

## Console or gateway offline

- Check container status (`docker compose ps`) or systemd units (`systemctl status aion.target`).
- Validate `.env` values for hostnames and ports.
- Review `gateway` and `control` service logs for configuration errors.
