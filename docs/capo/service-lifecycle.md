# CAPO native service lifecycle

Phase 5 adds reviewed systemd definitions for Runtime, Control, Gateway, and
Console plus an aggregate target. It does not change application code, Docker
Quickstart, authentication, public APIs, database schemas, or persistent data.

## Use on the Linux target

1. Copy `deploy/CAPO/CAPO.env.example` to `/etc/omertaos/omertaos.env`, replace
   placeholders outside Git, and restrict it to root and the `omertaos` group.
2. Run `deploy/CAPO/scripts/first-boot.sh --dry-run` and review the commands.
3. Run `first-boot.sh`; add `--start` only when immediate startup is intended.
4. Later use `run-all.sh` and `stop-all.sh` for the aggregate target. Inspect
   logs with `journalctl -u 'omertaos-*'` on the Linux host.

The order is Runtime -> Control -> Gateway -> Console. Control also requires
native PostgreSQL and Redis. Units run as the non-login `omertaos` account,
load the operator-owned environment file, and use bounded restart behavior.

## Security, migration, and rollback

No real secret is committed or printed. Units enable `NoNewPrivileges` and a
private temporary directory; application auth and permissions remain intact.
This phase has no schema or data migration. To roll back, stop
`omertaos.target`, disable it, restore the previous unit definitions if any,
and reload systemd. Preserve `/etc/omertaos/omertaos.env`, application state,
databases, and the service account unless separately approved and backed up.

The assets were statically validated on Windows. Native systemd behavior and
Linux path/ownership acceptance must be verified on the intended SSD host.
