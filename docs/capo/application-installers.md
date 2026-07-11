# CAPO application installers

Phase 4 adds native, non-service-starting installers for the canonical chain:

```text
console/ -> gateway/ -> control/ -> runtime-daemon/
```

## Behavior

- `install-python-control.sh` creates or reuses the Control virtual environment,
  installs the root project with its `control` extra, and imports
  `control.app.main:app` as a repeatable entrypoint check.
- `install-node-services.sh` checks Node.js 18+, installs and builds Gateway, then
  uses Console's committed `pnpm-lock.yaml` with `--frozen-lockfile`, generates
  its Prisma client, and builds Next.js. Gateway has no committed lockfile, so
  the script reports that limitation and uses `npm install` instead of invalid
  `npm ci` semantics.
- `install-rust-runtime.sh` performs a release build from
  `runtime-daemon/Cargo.toml` (locked when a `Cargo.lock` is present) and installs the binary in
  `/var/lib/omertaos/bin`. It neither starts Runtime nor supplies CLI flags.

All scripts accept `--root`, `--help`, and `--dry-run`; component-specific paths
can also be overridden. Defaults come from the CAPO environment contract. Run
OS/data setup first, then run these installers as an operator able to write the
checkout build directories and `/var/lib/omertaos`.

## Security and migration

The installers do not read or print application secrets, start services, alter
auth/permissions, or modify database schemas. Builds stay in the canonical
source directories; the only installed artifact is the reviewed Runtime binary.
No legacy path is moved or deleted, and Docker Quickstart remains unchanged.

## Validation and limitations

Windows validation is limited to static contracts, repository regression tests,
and available local builds. Native Debian/Ubuntu execution remains pending on
the intended Linux SSD host. A failed application install can be rolled back by
reverting this phase and rebuilding the virtual environment, Node outputs, or
Runtime binary from the prior commit; persistent data and configuration should
not be deleted.
