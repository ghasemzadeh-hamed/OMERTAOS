# Privacy and telemetry

AION-OS ships without telemetry by default. Administrators can opt in to anonymous metrics collection during the wizard summary step.

## Data collected (opt-in only)

- Installer mode and profile selection
- Hardware class (GPU vendor, NIC vendor)
- Success or failure of driver/security tasks
- No personal data or workload content

## Control plane

- Metrics are sent over HTTPS to the configured endpoint.
- Disable telemetry by unchecking the opt-in box or setting `AION_TELEMETRY=disabled` in `.env`.

## Logs

- Installer logs: `/var/log/aionos-installer.log`
- First boot logs: `/var/log/aionos-firstboot.log`
- Rotate logs with your existing log pipeline or configure `logrotate` entries under `/etc/logrotate.d/aionos`.
