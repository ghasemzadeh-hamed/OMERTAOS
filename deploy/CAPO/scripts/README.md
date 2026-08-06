# CAPO scripts

Phase 3 provides `install-os-packages.sh` and `install-data-services.sh`. Phase
4 adds the three application installers for Control, Gateway/Console, and the
Runtime daemon. Each supports `--help`, `--dry-run`, platform checks, and
repeatable validation. Lifecycle and validation scripts are added in phases 5
and 6.

Run the application installers from any directory after the repository is at
the configured `OMERTAOS_ROOT`:

```bash
bash deploy/CAPO/scripts/install-python-control.sh --dry-run
bash deploy/CAPO/scripts/install-node-services.sh --dry-run
bash deploy/CAPO/scripts/install-rust-runtime.sh --dry-run
```

The Python installer uses the root `pyproject.toml` `control` extra and validates
`control.app.main:app`. Console, Gateway, and Runtime use their committed
lockfiles; Gateway uses `npm ci`, and Runtime requires
`cargo build --locked --release`. Installers never start services or probe
unsupported Runtime CLI flags.

Phase 5 adds `setup-systemd.sh`, `first-boot.sh`, `run-all.sh`, and
`stop-all.sh`. They preserve `/etc/omertaos/omertaos.env`, provide help and
dry-run modes, and never execute systemd on the Windows automation host.

N7 adds the read-only `smoke-test.sh` for independent Native and Quickstart
checks. N8 adds versioned `update.sh`/`rollback.sh` plus canonical
`backup.sh`/`restore.sh` wrappers. Rollback atomically selects a verified
immutable release and never disables the target, deletes state, or downgrades
databases automatically.
See `../../../docs/capo/validation-recovery.md` for the acceptance matrix and
troubleshooting workflow.
`first-boot.sh` requires a release version and verified external backup, then
delegates build/migration/activation to N8. Services remain stopped unless the
operator supplies `--start`.

Every script follows the safety and idempotency contract in the parent README.
Linux-native commands must not be executed on the Windows automation host.
