# OMERTAOS native systemd units

N6 defines six canonical assets: the N5 one-shot install unit, four application
services, and `omertaos.target`. Boot ordering is:

```text
PostgreSQL + Redis
→ omertaos-install.service
→ Runtime
→ Control
→ Gateway
→ Console
```

The install unit runs the additive migration and fail-closed administrator
bootstrap before Runtime. It is `PartOf` the aggregate target, so a later target
restart performs the idempotent N5 checks again. It reads installer credentials
through the N5 scripts and never exposes them to long-running services.

Each application service loads non-secret `omertaos.env` plus exactly one
service-specific environment file. Runtime, Control, Gateway, and Console run as
the non-root `omertaos` account. They use built N4 artifacts directly rather
than package-manager start wrappers, apply read-only filesystem protection with
only explicitly required writable state paths, and restart at most three times
per 60-second window.

Install and verify without starting the stack:

```bash
bash deploy/native/scripts/install-systemd.sh --dry-run
bash deploy/native/scripts/install-systemd.sh
bash deploy/native/scripts/install-systemd.sh --check
```

Only `run.sh` starts `omertaos.target`; `stop.sh` stops that target without
stopping PostgreSQL, Redis, or deleting persistent data. `systemd-analyze verify`
is required before unit installation. Static Windows validation does not prove
Linux ownership, sandbox enforcement, boot ordering, journald output, or live
service readiness; those remain N7 acceptance items on a supported host.

N8 units resolve every application artifact through `/opt/omertaos/current`.
The versioned update/rollback scripts atomically change that symlink and retain
the prior immutable release at `/opt/omertaos/previous`.
