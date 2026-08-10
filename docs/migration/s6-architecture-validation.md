# Structure S6 architecture validation

Original execution: 2026-07-15

Reconciled: 2026-08-10 on branch `CAPO`

Status: **passed for Structure architecture validation; Native acceptance remains separate**

## R3 reconciliation

The historical dependency-resolution blocker is resolved on current CI evidence.
At commit `91921367cdfa600abb91710f7d699a183af800fa`, architecture, lint,
service-build, integration, security, Python tests, locked Cargo tests and the
locked Runtime release build passed in CI run
[`31358631289`](https://github.com/Hamedghz/OMERTAOS/actions/runs/31358631289).
The active Python suite reports 164 passed and 2 skipped locally, and the full
architecture suite reports 63 passed. Gate S6 is closed for repository
architecture validation. Linux/systemd execution, reboot, live smoke, update,
rollback and isolated restore remain Native acceptance work and are not inferred
from CI.

## Historical outcome

## Outcome

S6 revalidated Structure as one connected migration rather than accepting the
earlier phase reports independently. The prospective working tree now contains
only the canonical top-level owners defined by `STRUCTURE.md`. Console and the
optional Desktop Shell call Gateway only; Gateway owns the Control boundary and
Control owns Runtime orchestration.

At the original execution date, the repository was not authorized to start N1
because compilation had not run. That historical restriction is superseded by
the R3 reconciliation above; current Native work still requires its own host
gate and explicit phase approval.

## S6 corrections and migration

- Resolved the S0 `UNKNOWN` roots without discarding content:
  - moved Desktop Shell to `console/desktop-shell/`;
  - moved Native profile inputs to `deploy/native/env/profiles/`;
  - moved Cluster placeholders to `docs/architecture/cluster/`;
  - preserved inactive placeholders, broken links and generated artifacts under
    `docs/migration/evidence/`.
- Removed Desktop Shell and Compose configuration that exposed direct Control
  endpoints to presentation clients. Control health is now read from Gateway's
  dependency response.
- Corrected the S3 false-negative schema audit. Authored contracts now live only
  under `schemas/v1/`, and generated Python bindings only under
  `shared/generated/`. Former byte-identical aliases are migration evidence.
- Retired eight uncollectable pre-canonical tests from the active suite without
  restoring the removed `os.control`, `os.kernel`, `aion.cli`, or `cli`
  namespaces. Their source is preserved under migration evidence.
- Restored a working tracked-root audit, bounded the cleanup scanner so generated
  dependency/build trees are ignored, and repaired Gateway/Bridge lint and test
  entrypoints.
- Replaced independent CAPO smoke/rollback copies with thin wrappers around
  `deploy/native/scripts/`, leaving one operational source of truth for N1.
- Moved superseded architecture plans/audits under migration evidence so current
  documentation does not describe retired roots as active owners.

No database schema, record, secret, host package, systemd state, container,
persistent volume or production environment was changed.

## Validation evidence

Repository-owned checks completed successfully:

- prospective canonical-root structure audit;
- complete active Python suite and architecture completion gate;
- Console lint, unit tests and production build;
- Gateway lint, six root integration tests and TypeScript build;
- Windows Bridge Server typecheck/tests/build and Bridge UI build;
- Desktop Shell typecheck and production build;
- Compose configuration rendering for canonical Quickstart, Local, Full,
  Observability, vLLM and K2 example files;
- CAPO static contracts, PowerShell parsing and Bash syntax;
- Cargo formatting and no-dependency metadata;
- backup SHA-256 comparison and `git bundle verify`.

Runtime `cargo test` remains blocked because this host cannot connect to
`index.crates.io:443` or `static.crates.io:443`, and the local Cargo registry has
no cached source packages. Offline mode therefore cannot resolve `anyhow`.

## Security notes

- No Console source, Desktop Shell capability/CSP, or Console Compose service
  receives a direct Control or Runtime endpoint.
- Gateway test credentials are fixed placeholders injected only by the test
  runner; production configuration still fails closed when the admin token is
  absent.
- No destructive database, filesystem, deployment or service-lifecycle command
  was run by S6.

## Rollback and recovery

The external recovery snapshot at
`D:/GHASEMZADEH/P/OMERTAOS-backups/capo/20260711-161030` was reverified before
the S6 migrations. Its repository bundle and source ZIP hashes match
`SHA256SUMS.txt`, and `git bundle verify` reports complete history.

Before commit, rollback is the reviewed reverse of the S6 file moves and edits;
the working tree itself remains the review boundary. After a future commit,
revert that single Structure commit rather than recreating legacy owners or
deleting persistent state. Native rollback continues to preserve source,
`/etc/omertaos/omertaos.env`, `/var/lib/omertaos`, accounts and databases.

## Historical N1 entry condition

The original entry condition required a reproducible compiled Runtime test. It
is now satisfied by the tracked Cargo lockfile and locked CI test/build. This
report still does not start Native work, install packages, launch services or
deploy.
