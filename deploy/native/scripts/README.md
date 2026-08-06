# OMERTAOS native scripts

N2 owns the read-only `preflight.sh`, the reviewed APT manifest under
`../packages/`, and `install-os-packages.sh`. The installer supports `--check`
and `--dry-run`, skips packages already installed, creates only the N1 account
and paths, and never installs or starts PostgreSQL/Redis servers. It does not
add third-party package repositories: if the selected distro repository cannot
supply the N1 Python 3.11/3.12 and Node 22 contract, provision a reviewed
toolchain source first and re-run `--check`.

N3 owns `install-data-services.sh` and `../env/validate_data_env.py`. It installs
PostgreSQL/Redis servers, requires loopback-only listeners and Redis snapshot
persistence, and creates separate Control and Console roles/databases only when
absent. It reads the root-only `installer.env` without shell sourcing and checks
that both service DSNs carry the same URL-encoded credentials. `--check` is
read-only. Schema migrations and bootstrap belong to N5.

N4 owns four independent application installers: `install-control.sh`,
`install-gateway.sh`, `install-console.sh`, and `install-runtime.sh`. Builds run
as the non-root `omertaos` account; cache and Runtime target data stay under
`/var/lib/omertaos`. Each supports `--check` and verifies its installed artifact
without starting a service. The former three script names remain thin wrappers.
Lifecycle and validation scripts are handled by later stages.

N5 owns `migrate-database.sh` and `bootstrap-admin.sh`. Migration applies only
the additive Control metadata and committed Console Prisma migrations, then
checks status. Bootstrap requires explicit root-only admin credentials, creates
an administrator only for an empty user table, and never rotates an existing
password. Both scripts support read-only `--check` and redact secrets in dry-run
output.

N6 owns `install-systemd.sh`, `run.sh`, and `stop.sh`. Installation verifies six
canonical units, environment permissions, and N4 artifacts before enabling only
the aggregate target. It never starts a service. The run/stop commands operate
only on `omertaos.target`; PostgreSQL and Redis are dependencies but remain
outside application lifecycle control.

N7 owns the read-only Native mode of `smoke-test.sh`. It validates data-service
readiness, the N5 one-shot result, N6 service state, Runtime TCP health, listener
exposure, service JSON payloads, the canonical Console/Gateway/Control chain,
restart counts, and journald visibility. It never starts or repairs the stack.

N8 owns `update.sh` and `rollback.sh`. Update requires an external non-empty
backup verified by `restore.sh`, builds a versioned immutable release, writes a checksum manifest, runs
forward-only N5 migration/bootstrap, and atomically changes `current` and
`previous`. Rollback verifies the manifest before changing those links. Both
serialize lifecycle changes with `flock`, preserve `/etc` and `/var/lib` state,
and never delete releases or reverse database migrations automatically.
`backup.sh` creates versioned PostgreSQL/Redis/config artifacts plus a SHA-256
manifest; restore defaults to verification and refuses unreviewed replacement.

Run the application installers from any directory after the repository is at
the configured `OMERTAOS_ROOT`:

```bash
bash deploy/native/scripts/install-control.sh --dry-run
bash deploy/native/scripts/install-gateway.sh --dry-run
bash deploy/native/scripts/install-console.sh --dry-run
bash deploy/native/scripts/install-runtime.sh --dry-run
```

N2 examples:

```bash
bash deploy/native/scripts/preflight.sh --profile lite
bash deploy/native/scripts/install-os-packages.sh --profile lite --dry-run
bash deploy/native/scripts/install-os-packages.sh --profile lite --check
```

N3 examples (on the intended Linux host only):

```bash
python3 deploy/native/env/validate_data_env.py
bash deploy/native/scripts/install-data-services.sh --profile lite --dry-run
bash deploy/native/scripts/install-data-services.sh --profile lite
bash deploy/native/scripts/install-data-services.sh --profile lite --check
```

Control uses the root `pyproject.toml` `control` extra and validates
`control.app.main:app`. Gateway uses its committed `package-lock.json` with
`npm ci`; Console uses `pnpm-lock.yaml` with `--frozen-lockfile`. Runtime refuses
an unlocked build and uses `cargo build --locked --release` into
`/var/lib/omertaos/build/runtime`. None of these commands runs N5 migrations.
Console pins pnpm and commits an explicit `allowBuilds` policy for only Prisma,
bcrypt, esbuild, and the native resolver packages required by its locked graph;
unreviewed dependency lifecycle scripts fail installation.

The lifecycle set includes `install-systemd.sh`, `first-boot.sh`, `run.sh`,
`stop.sh`, `update.sh`, and `rollback.sh`. They preserve `/etc/omertaos` and
`/var/lib/omertaos`, provide help/dry-run or check modes where applicable, and
never execute systemd on the Windows automation host. See
`../../../docs/capo/validation-recovery.md` for the acceptance matrix and
recovery workflow.
`first-boot.sh` leaves services stopped unless the operator supplies `--start`.

Every script follows the safety and idempotency contract in the parent README.
Linux-native commands must not be executed on the Windows automation host.
