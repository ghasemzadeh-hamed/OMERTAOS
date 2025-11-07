# AIONOS Installer Bridge

The installer bridge runs with elevated permissions to execute hardware probes and
installation tasks. It exposes a narrow HTTP API (`/task`) that accepts a JSON
payload containing the task name and parameters.

## Permission model

- The process should be launched under root when destructive actions (disk
  partitioning, user creation, bootloader installation) are required.
- Disk changing operations are gated by both `process.getuid() === 0` and the
  `AIONOS_ALLOW_INSTALL=1` environment variable. Without both, the bridge returns
  `not-allowed` to ensure web or desktop sessions cannot format disks.
- Security and driver tasks require root but do not check the install flag to
  support first boot remediation.
- Profile read/write tasks only expose allow-listed operations and must never
  permit arbitrary command execution.

The Next.js wizard communicates with this service via the `/api/installer/*`
proxy endpoints so the same UI can run in web, desktop shell, or kiosk mode.
