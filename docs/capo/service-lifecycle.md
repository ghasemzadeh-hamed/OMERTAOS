# CAPO native service lifecycle

Phase 5/N6 adds reviewed systemd definitions for the N5 one-shot install phase,
Runtime, Control, Gateway, and Console plus an aggregate target. It does not change application code, Docker
Quickstart, authentication, public APIs, database schemas, or persistent data.

## Use on the Linux target

1. Copy `deploy/CAPO/CAPO.env.example` to `/etc/omertaos/omertaos.env`, replace
   placeholders outside Git, and restrict it to root and the `omertaos` group.
2. Run `deploy/CAPO/scripts/first-boot.sh --version VERSION --backup PATH
   --dry-run` and review the commands.
3. Run the same command without `--dry-run`; add `--start` only when immediate
   startup is intended. First boot installs N2/N3 prerequisites, then delegates
   release build, migration, activation, and systemd installation to N8.
4. Later use `run-all.sh` and `stop-all.sh` for the aggregate target. Inspect
   logs with `journalctl -u 'omertaos-*'` on the Linux host.

The order is PostgreSQL/Redis -> Install -> Runtime -> Control -> Gateway ->
Console. Long-running units run as the non-login `omertaos` account and load the
common environment plus their own service-specific file. The root-only installer
environment is available only to the one-shot N5 scripts.

## Security, migration, and rollback

No real secret is committed or printed. Units enable `NoNewPrivileges`, strict
filesystem protection, and a private temporary directory; application auth and
permissions remain intact. The one-shot unit applies only the reviewed N5
migration/bootstrap behavior. N8 rollback verifies the immutable release
manifest and atomically switches `/opt/omertaos/current` and
`/opt/omertaos/previous`. It does not disable the target, delete releases/state,
or reverse database migrations. Preserve `/etc/omertaos`,
`/var/lib/omertaos`, databases, and the service account.

The assets were statically validated on Windows. Native systemd behavior and
Linux path/ownership acceptance must be verified on the intended SSD host.
