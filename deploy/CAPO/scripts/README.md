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
`control.app.main:app`. Console uses the committed `pnpm-lock.yaml`; Gateway
currently has no committed lockfile and therefore uses `npm install` explicitly.
The Rust installer uses `cargo build --locked --release` when a lockfile exists,
reports the repository's current missing-lockfile limitation otherwise, and
installs `runtime-daemon` without starting it or probing unsupported CLI flags.

Every script follows the safety and idempotency contract in the parent README.
Linux-native commands must not be executed on the Windows automation host.
