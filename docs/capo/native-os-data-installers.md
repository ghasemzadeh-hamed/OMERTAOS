# CAPO native OS and data installers

Phase 3 adds reviewed, idempotent installers for a Debian/Ubuntu Linux SSD host.
They are stored on Windows but were not executed there.

## Prerequisites and order

1. Review `deploy/CAPO/CAPO.env.example` and create
   `/etc/omertaos/omertaos.env` outside Git with mode `0640` or stricter.
2. Replace `CAPO_POSTGRES_PASSWORD=CHANGE_ME` with a generated secret and make
   the file readable only by root and the `omertaos` group.
3. Preview package/account/path work:
   `bash deploy/CAPO/scripts/install-os-packages.sh --dry-run`.
4. Run the OS installer on the supported Linux host, then preview data setup:
   `bash deploy/CAPO/scripts/install-data-services.sh --dry-run`.
5. Run the data installer only after reviewing its preview.

Use `--env-file PATH` to validate a staged environment file. `--help` is
non-mutating. Both installers reject non-Debian/Ubuntu hosts, stop on errors,
and require explicit privilege escalation when not run as root.

## Idempotency and database behavior

The OS installer queries dpkg and installs only missing reviewed packages. It
creates the non-root `omertaos` account only when absent and reconciles the two
owned directories without touching the repository checkout.

The data installer enables native PostgreSQL and Redis, requires readiness and
Redis `PONG`, and creates the configured PostgreSQL login role/database only
when absent. It does not reset an existing role password or alter an existing
database owner. An owner mismatch fails for human review. It does not run
application migrations or seeders; those remain a later, explicitly reviewed
step after the application installation contract is complete.

## Optional service degraded mode

MongoDB, Qdrant, and MinIO are neither installed nor started by Phase 3. Their
`CAPO_*_ENABLED` flags remain `false`. Features requiring a disabled service
must report an unavailable/degraded capability and must not silently substitute
volatile storage or bypass Control. Enable each service only after separately
installing it, configuring non-placeholder credentials, and adding readiness
proof on the target host.

## Security and rollback

Secrets remain in `/etc/omertaos/omertaos.env`, never command-line arguments,
logs, or Git. PostgreSQL identifiers are restricted before reaching `psql`, and
values use psql quoting. The scripts contain no disk formatting, partitioning,
repository deletion, blanket error suppression, or Docker dependency.

Rollback for this phase means stopping/disabling the two native services if the
operator enabled them. Do not delete the PostgreSQL role, database, Redis data,
service account, or state directories automatically. Any data removal requires
separate backup evidence and explicit human approval.
