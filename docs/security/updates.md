# Updates and CVE response

AION-OS treats security updates as a first-boot requirement and encourages regular maintenance windows.

## First boot

- Runs `apt-get update` and `apt-get upgrade`
- Refreshes snaps when available
- Installs profile-specific packages (drivers, ML tooling)
- Logs actions to `/var/log/aionos-firstboot.log`

## Scheduled maintenance

1. Configure unattended upgrades if your policy allows (`sudo apt-get install unattended-upgrades`).
2. For managed fleets, orchestrate updates via Ansible or Landscape, invoking `core/firstboot/aionos-firstboot.sh` in dry-run mode for validation.
3. Monitor Canonical USNs and vendor advisories for NVIDIA/AMD/Intel drivers.

## CVE response SLA

| Severity | Target response                    |
| -------- | ---------------------------------- |
| Critical | Patch and release within 24 hours  |
| High     | Patch within 72 hours              |
| Medium   | Patch in the next scheduled update |
| Low      | Evaluate monthly                   |

## Reporting

- Report vulnerabilities privately to the contacts in [SECURITY.md](../../SECURITY.md).
- Include hardware details (`lspci`, `lsblk`) and log excerpts when filing reports.
