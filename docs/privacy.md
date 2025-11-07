# Privacy and telemetry

AION-OS ships without telemetry by default. Administrators must explicitly opt in via the installer prompts, the Glass console wizard, or the `AION_TELEMETRY_OPT_IN` environment variable before any metrics are emitted.

## Data collected (opt-in only)

- Installer mode and profile selection (when enabled)
- Hardware class (GPU vendor, NIC vendor)
- Success or failure of driver/security tasks
- No personal data or workload content

## Control plane

- Metrics are sent over HTTPS to the configured endpoint.
- Leave telemetry disabled by default (the installer prompt defaults to "No" and the console toggle is unchecked).
- Opt in by setting `AION_TELEMETRY_OPT_IN=true` and, optionally, `AION_TELEMETRY_ENDPOINT` in `.env` or through the setup wizard.

## Logs

- Installer logs: `/var/log/aionos-installer.log`
- First boot logs: `/var/log/aionos-firstboot.log`
- Rotate logs with your existing log pipeline or configure `logrotate` entries under `/etc/logrotate.d/aionos`.
