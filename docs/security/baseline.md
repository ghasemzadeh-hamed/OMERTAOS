# Security baseline

AION-OS ships with a configurable hardening baseline. The table below maps levels to actions.

| Level    | Actions                                                                  |
| -------- | ------------------------------------------------------------------------ |
| none     | Security updates only                                                    |
| standard | `apt-get upgrade`, UFW enabled, Fail2Ban enabled                         |
| cis-lite | All standard actions plus Auditd, stricter SSH, and log retention tuning |

## Controls

- **Updates**: `aionos-firstboot` runs `apt-get update` and `apt-get upgrade` with unattended retries.
- **Firewall**: UFW enforces deny-by-default rules with service-specific exceptions (`ssh`, `https`).
- **Fail2Ban**: Enabled for SSH and gateway endpoints when `standard` or `cis-lite` is active.
- **Auditd**: Enabled for `cis-lite` to track auth events and configuration changes.
- **Logging**: Installer and first-boot logs live in `/var/log/aionos-installer.log` and `/var/log/aionos-firstboot.log`.

## Customisation

1. Place overrides in `/etc/aionos/hardening.d/*.conf`.
2. Use systemd drop-ins to tweak service unit security contexts.
3. Document deviations in your internal security playbook.
