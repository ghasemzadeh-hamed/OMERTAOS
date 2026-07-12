# CAPO acceptance report

Date: 2026-07-12 (Asia/Tehran)

Branch: `capo`

Baseline: `b4021a4327d63b8db0c0e0f87267dec28907cb36`

Phase 6 head reviewed: `d4e96723b5b6341af5c3b4c899d9fdaca2054331`

## Decision

The seven-phase CAPO implementation is **conditionally accepted for human
review and Linux-host validation**. Static contracts, configuration rendering,
application entrypoint checks, Gateway/Console builds, and the verified recovery
baseline pass. Production use, permanent legacy-path retirement, merge, and
deployment are not accepted by this report.

Native systemd acceptance remains pending on the intended Debian/Ubuntu SSD
host. Running Docker Quickstart acceptance also remains pending because the
local Docker daemon did not respond during Phases 6 and 7. These two gates are
independent and neither may be inferred from static validation.

## Delivered scope

- Verified external Git/source backup and reconstruction map.
- Non-secret CAPO environment and idempotency/security contract.
- Debian/Ubuntu, PostgreSQL, and Redis installers with dry-run behavior.
- Canonical Control, Gateway, Console, and Runtime build/install scripts.
- Four non-root systemd services, aggregate target, and lifecycle scripts.
- Read-only Native/Quickstart smoke checks, contract tests, troubleshooting,
  and non-destructive rollback.

Across Phases 1–6, CAPO added 29 tracked files with 1,529 lines relative to the
baseline. No existing source, schema, table, data, legacy path, or public API was
removed or moved.

## Evidence

| Check | Result | Notes |
|---|---|---|
| Backup SHA-256 and Git bundle | pass | Three hashes match; bundle reports complete history |
| CAPO Bash syntax and `--help` | pass | All reviewed scripts via Git Bash |
| CAPO PowerShell contracts | pass | Ports, env, systemd hardening, rollback, forbidden commands |
| Quickstart/Local Compose rendering | pass | Both `config --quiet` checks |
| Architecture tests | pass | `14 passed in 0.95s` in final review |
| Control import | pass | `control.app.main:app` |
| Gateway TypeScript build | pass | `tsc -p tsconfig.json` |
| Console production build | pass with warnings | Missing local Prisma generation/DB URL; stale browser data |
| Runtime metadata | pass | Cargo manifest resolves without dependency download |
| Runtime release build | blocked | `index.crates.io:443` unavailable after retries |
| Full Python regression | blocked by legacy collection | 11 import errors for removed `os.control`, `os.kernel`, `aion`, and CLI paths |
| Native Linux smoke | pending | Requires intended Linux SSD/systemd host |
| Running Quickstart smoke | pending | Docker daemon did not respond; stack was not mutated |

No coverage report was generated because CAPO changes deployment assets and
documentation rather than application runtime code.

## Security and data review

- Services run as the dedicated non-login `omertaos` account and include
  `NoNewPrivileges` and `PrivateTmp`.
- Real secrets remain outside Git in `/etc/omertaos/omertaos.env`.
- PostgreSQL and Redis are required; optional stores default disabled.
- Static scanning found no executable destructive disk, Git move/removal,
  `DROP`, or `TRUNCATE` command in CAPO assets.
- Rollback preserves source, configuration, accounts, databases, volumes, and
  persistent state.

## Open acceptance gates

1. Run installers twice on a disposable Debian/Ubuntu SSD host and confirm the
   second execution is idempotent.
2. Run `first-boot.sh --start`, Native smoke, journald review, reboot recovery,
   stop/start, and rollback preview/execute with an operator present.
3. Start Quickstart, run its smoke test, verify Console → Gateway → Control →
   Runtime, and stop it without deleting volumes.
4. Restore the external backup in an isolated environment and reconcile the
   resulting commit and data checks.
5. Resolve or formally quarantine the legacy Python tests before treating the
   repository-wide regression suite as green.

Until all relevant gates pass, the permanent-deletion gate stays closed and
human review is required before merge or any production use.
