# OMERTAOS Native deployment contract

## N0 acceptance host

Before N1, create and validate the disposable Hyper-V Ubuntu 24.04 host with
`host/New-OmertaN0Host.ps1`. The N0 contract and evidence format are documented
in `docs/native/n0-acceptance-host.md`. N0 prepares only the host, restricted
SSH access, `/etc/omertaos` ownership boundary, exact release checkout and base
checkpoint; it does not install or start OMERTAOS services.

If Hyper-V is unavailable, `host-sim/Invoke-N0Simulation.ps1` can prepare an
experimental Ubuntu 24.04 systemd/cgroups/SSH container for contract testing.
This fallback is isolated on an internal Docker network and is not Native host
or reboot acceptance.

N1 defines the environment boundary for a future non-containerized installation.
It does not install packages, create databases, modify systemd, or start services.
The executable host check is `scripts/validate-environment.sh`; the Docker N0
fallback runs it through `host-sim/Invoke-N1Simulation.ps1`. Missing tools and
paths owned by N2/N4/N8 are reported as deferred, never as installed evidence.

## Supported baseline

| Component | N1 contract |
| --- | --- |
| OS | Debian 12; Ubuntu 22.04 or 24.04 LTS; systemd |
| CPU | x86_64 or arm64; Linux cgroups v2 required for Runtime isolation |
| Python | 3.11 or 3.12, isolated Control virtualenv |
| Node.js | 22 LTS with Corepack/pnpm for Console and npm for Gateway |
| Rust | stable toolchain; the locked Runtime dependency graph must build before N4 acceptance |
| PostgreSQL / Redis | Local loopback services; exact packages and initialization belong to N2/N3 |

N8 stores immutable code releases under `/opt/omertaos/releases/<version>` and
exposes the active one through `/opt/omertaos/current`; `/opt/omertaos/previous`
records the prior code release. Persistent state is `/var/lib/omertaos`, logs
are `/var/log/omertaos`, and configuration is `/etc/omertaos`. Upgrade backups
must be external to both `/opt/omertaos` and `/var/lib/omertaos`. Installers
must never erase state, configuration, releases, or backups.

`OMERTAOS_ROOT` is always `/opt/omertaos/current`; installers receive an
explicit staging/release root while building. Fresh installation must not build
into a parallel mutable checkout.

## Environment files and permissions

Copy `env/omertaos.env.example` to `/etc/omertaos/omertaos.env`, then copy each
service template without the `.example` suffix. The common file contains no
secrets. `runtime.env`, `control.env`, `gateway.env`, and `console.env` are
`0640 root:omertaos`; `installer.env` is `0600 root:root` and must never be
loaded by a long-running service. Replace every `CHANGE_ME` outside Git.

N6 systemd units load the common file plus exactly one service-specific file per
long-running service. The root-only installer file is consumed only by the N5
one-shot scripts and is never loaded into Runtime, Control, Gateway, or Console.
These templates and units are statically validated contracts until N7 exercises
them on a supported Linux systemd host.

Console traffic terminates at Gateway. Only Gateway receives Control addresses;
only Control receives the Runtime endpoint. Control and Runtime bind to loopback.
The Console `DATABASE_URL` is limited to its existing authentication store and
does not authorize domain persistence or direct Control/Runtime access.

## Profiles, optional services, and validation

Choose one non-secret overlay from `env/profiles`: `lite`, `full`, or
`enterprise`. Optional MongoDB, Qdrant, and MinIO capabilities default to off in
all profiles; N3 may enable them only after installation, credentials, health,
backup, and rollback behavior are proven.

Validate committed templates:

```bash
python3 deploy/native/env/validate.py
```

Validate rendered `/etc/omertaos` files and reject placeholders:

```bash
python3 deploy/native/env/validate.py --directory /etc/omertaos --strict
```

Runtime/systemd installation, database migration, live health checks, backup
restore, and rollback remain unproven until their later Native stages run on a
supported Linux host. N4 acceptance requires the committed Cargo lock to pass
locked tests and a release build with the target host linker; metadata or
dependency-resolution success alone does not satisfy that gate.

## N2 package installation

N2 provides a read-only host preflight and an idempotent APT installer:

```bash
bash deploy/native/scripts/preflight.sh --profile lite
bash deploy/native/scripts/install-os-packages.sh --profile lite --dry-run
bash deploy/native/scripts/install-os-packages.sh --profile lite
bash deploy/native/scripts/install-os-packages.sh --profile lite --check
```

The reviewed manifest is `packages/apt-build-packages.txt`. N2 installs build
tools and PostgreSQL/Redis clients, but deliberately excludes the database
servers so package installation cannot start persistent services ahead of N3.
It also installs `rsync` and `util-linux` so N8 release copying and lifecycle
locking are guaranteed by the same reviewed package contract.
It also refuses to report success unless the installed Python and Node versions
match N1. Node 20 is EOL and is not accepted. No third-party repository is added
automatically; repository trust is an operator decision and must be reviewed
separately. Ubuntu 22.04 therefore requires a reviewed Python 3.11/3.12 source,
and any supported OS whose stock repository lacks Node 22 requires a reviewed
Node source before the mutating installer is run.

## N3 native data services

N3 installs and activates only the required PostgreSQL and Redis services. Copy
the N1 templates to `/etc/omertaos`, replace and URL-encode the two distinct
PostgreSQL passwords in their service DSNs, then secure `installer.env` as
`0600 root:root` and the Control/Console files as `0640 root:omertaos`.

```bash
python3 deploy/native/env/validate_data_env.py
bash deploy/native/scripts/install-data-services.sh --profile lite --dry-run
bash deploy/native/scripts/install-data-services.sh --profile lite
bash deploy/native/scripts/install-data-services.sh --profile lite --check
```

The installer never rotates an existing password, changes ownership, or creates
application schemas. A mismatch fails closed and requires operator review. N5
owns Prisma/Control migrations and bootstrap. Redis must answer `PONG`, retain
an RDB save policy, and expose no non-loopback listener. PostgreSQL must be
ready on `127.0.0.1:5432`; both configured accounts must log in successfully.
During package installation, a temporary `policy-rc.d` guard prevents automatic
service start. The installer removes only its own marked guard, validates the
effective PostgreSQL/Redis bind configuration, and then starts the services.

MongoDB, Qdrant, and MinIO remain explicit degraded capabilities for now,
including Full/Enterprise profiles. Enabling one requires a separately reviewed
package source, credential contract, health check, backup, and rollback proof.
N3 rollback never drops roles/databases or removes `/var/lib` data: stop/disable
the two services only after human approval, and preserve their packages/data.

## N4 build and install

N4 separates the four canonical service installers. Run them after N2/N3 and
before N5; they build artifacts but never start systemd units or migrate data:

```bash
bash deploy/native/scripts/install-control.sh --dry-run
bash deploy/native/scripts/install-gateway.sh --dry-run
bash deploy/native/scripts/install-console.sh --dry-run
bash deploy/native/scripts/install-runtime.sh --dry-run
```

Actual builds execute as `omertaos`, never as root. The checkout must therefore
allow `omertaos` to write only the component build outputs (`node_modules`,
`dist`, and `.next`); writable cache/venv/Cargo target state belongs under
`/var/lib/omertaos`. Gateway and Console require committed lockfiles. Runtime
requires `runtime-daemon/Cargo.lock` and fails closed when the registry cannot
resolve it. Re-run every installer with `--check` before N5.

N4 rollback rebuilds the four artifacts from the prior reviewed revision. It
does not remove configuration, databases, service accounts, or persistent data;
versioned release switching is implemented later in N8.

## N5 database install phase

After all N4 artifacts exist, apply the two distinct database schemas and then
bootstrap the first Console administrator:

```bash
bash deploy/native/scripts/migrate-database.sh --dry-run
bash deploy/native/scripts/migrate-database.sh
bash deploy/native/scripts/migrate-database.sh --check
bash deploy/native/scripts/bootstrap-admin.sh --dry-run
bash deploy/native/scripts/bootstrap-admin.sh
bash deploy/native/scripts/bootstrap-admin.sh --check
```

Set `OMERTAOS_CONSOLE_ADMIN_EMAIL`, `OMERTAOS_CONSOLE_ADMIN_PASSWORD`, and an
optional `OMERTAOS_CONSOLE_ADMIN_NAME` in root-only `installer.env`. Placeholder,
default, or passwords shorter than 16 characters are rejected. Bootstrap creates
the configured administrator only when the Console user table is empty; repeated
runs never overwrite a password or add an administrator to an established user
store. Migration uses Control's additive SQLAlchemy metadata and Console's
committed Prisma migrations. N5 contains no downgrade, drop, truncate, seed, or
service-start operation. Database rollback means restoring a verified backup or
applying a separately reviewed forward migration; the installer never reverses
schema automatically.

## N6 systemd units

N6 installs a one-shot N5 unit, four non-root application services, and the
aggregate target. `install-systemd.sh` validates environment ownership/modes,
N4 artifacts, and all unit files with `systemd-analyze verify` before copying
anything. It enables the target but does not start it.

```bash
bash deploy/native/scripts/install-systemd.sh --dry-run
bash deploy/native/scripts/install-systemd.sh
bash deploy/native/scripts/install-systemd.sh --check
bash deploy/native/scripts/run.sh
bash deploy/native/scripts/stop.sh
```

Only the explicit `run.sh` command starts the stack. Stopping the aggregate
target leaves PostgreSQL, Redis, configuration, credentials, backups, and
persistent data untouched. Live boot/readiness and journal validation belong to
N7.

## N7 Native smoke tests

N7 is a read-only acceptance probe for an already running Native stack:

```bash
bash deploy/native/scripts/smoke-test.sh --mode native --timeout 5
```

It requires PostgreSQL and Redis readiness, a successful exited N5 install unit,
all four active application services, an active/enabled aggregate target, the
Runtime binary healthcheck, loopback-only Runtime/Control listeners, healthy
JSON payloads, healthy Gateway dependencies, the Console-to-Gateway-to-Control
health chain, bounded restart counts, and at least one journald entry per unit.
It never starts, stops, reloads, migrates, bootstraps, or changes configuration.

Passing tests on Windows or rendering unit files is not N7 acceptance. The probe
must complete on the intended supported Linux host after N4, N5, and N6 live
gates pass. A Runtime gRPC listener proves readiness only; sandbox execution
remains fail-closed until its separate isolation acceptance is completed.

## N8 update and rollback

N8 builds each version into a new immutable release directory, records checksums
for critical lockfiles and artifacts, applies forward-only N5 migrations, and
then atomically switches `current`. An existing non-empty backup outside the
installation and state roots is mandatory before migration:

```bash
bash deploy/native/scripts/backup.sh --dest /mnt/backup --dry-run
bash deploy/native/scripts/backup.sh --dest /mnt/backup
bash deploy/native/scripts/restore.sh --backup /mnt/backup/omertaos-TIMESTAMP
```

`restore.sh` defaults to read-only verification: it checks the SHA-256 manifest,
both PostgreSQL custom dumps, the Redis RDB header, and configuration archive.
Live restore remains fail-closed until an operator reviews the target database
mapping; update accepts only a backup that passes this canonical verification.

```bash
bash deploy/native/scripts/update.sh \
  --version 1.2.3 \
  --source /srv/omertaos-source \
  --backup /mnt/backup/omertaos-before-1.2.3 \
  --dry-run
bash deploy/native/scripts/update.sh \
  --version 1.2.3 \
  --source /srv/omertaos-source \
  --backup /mnt/backup/omertaos-before-1.2.3 \
  --start
```

The update refuses to overwrite an existing version. It serializes lifecycle
changes with a lock, builds all four N4 services inside the release, preserves
configuration and state outside it, and runs N7 after a live switch. If unit
installation, startup, or smoke validation fails, the code symlink is restored
to the old release. Applied migrations remain forward-only.

Preview or validate a rollback target before switching:

```bash
bash deploy/native/scripts/rollback.sh --check
bash deploy/native/scripts/rollback.sh --dry-run
bash deploy/native/scripts/rollback.sh --start
```

Rollback verifies the selected release checksum manifest and atomically swaps
`current`/`previous`. It never disables the target, deletes a release, rewrites
configuration, removes state, or automatically downgrades a database. When a
schema is incompatible with the prior code, restore the verified external
backup only through a separately reviewed operator recovery procedure.

For the first installation, `first-boot.sh` runs only N2/N3 directly and then
delegates N4 through N8 to `update.sh`, ensuring `current` exists before systemd
validation:

```bash
bash deploy/native/scripts/first-boot.sh \
  --version 1.2.3 \
  --backup /mnt/backup/omertaos-before-1.2.3 \
  --dry-run
```
