# CAPO acceptance report

## R3 current reconciliation — 2026-08-10

Official branch `CAPO` is synchronized at evidence commit
`91921367cdfa600abb91710f7d699a183af800fa`. The current lockfiles are tracked:

| Lockfile | SHA-256 |
|---|---|
| `runtime-daemon/Cargo.lock` | `9C7EBC387FEF54CB7C2BBC70F96EA2DDF690F7636D18175FA251B96D5D5433F6` |
| `gateway/package-lock.json` | `CECAD9E18FB37754EBDF9CAC078BDC0A10CFE939365651CEB84160746866D55F` |
| `console/pnpm-lock.yaml` | `98FCA5264683D58F5274C14A62971FE56679AC7AD0C3A61C49722CFB0D4555B1` |

CI run [`31358631289`](https://github.com/Hamedghz/OMERTAOS/actions/runs/31358631289)
passed architecture, lint, all service builds, Python and locked Cargo tests,
the locked Runtime release build, integration, security, seven image builds and
six architecture-independent checks. The remaining emulated arm64 Console image
job stayed in progress for more than three hours. R3 moves arm64 image builds to
the native `ubuntu-24.04-arm` runner and retains the locked Linux Runtime binary
plus its SHA-256 as a CI artifact.

Current Gate status:

| Gate | Status | Current evidence |
|---|---|---|
| S2 Core Migration | passed | Four service builds plus locked Runtime test/release build |
| S3 Supporting Migration | passed | 63 architecture tests and deterministic retired-root guards |
| S5 Legacy Retirement | passed (repository scope) | Explicit approval, absent retired roots, no executable dependencies |
| S6 Architecture Validation | passed | Full Python and architecture suites plus CI boundaries |
| Gate R | pending | Requires the R3 commit to be clean, pushed, fully green and architecture-complete |
| Native live acceptance | pending | No current Ubuntu/systemd reboot/smoke/update/rollback/restore evidence |
| Docker live acceptance | pending | Image build is not running-stack smoke/parity evidence |

The historical report below remains immutable evidence of its original review.

> Historical snapshot: this report records the 2026-07-12 CAPO review. The
> current Native N1-N8 contract supersedes its missing-lockfile and stop/disable
> rollback descriptions. Gateway and Runtime lockfiles now exist; N8 uses
> immutable releases, canonical backup verification, and atomic code rollback.
> Live Linux/systemd, Runtime build, smoke, update, and restore acceptance remain
> pending until rerun and recorded on the intended host.

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
  canonical backup verification, and immutable release rollback.

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
2. Run `first-boot.sh --version VERSION --backup PATH --start`, Native smoke,
   journald review, reboot recovery, stop/start, update, and rollback
   preview/execute with an operator present.
3. Start Quickstart, run its smoke test, verify Console → Gateway → Control →
   Runtime, and stop it without deleting volumes.
4. Restore the external backup in an isolated environment and reconcile the
   resulting commit and data checks.
5. Resolve or formally quarantine the legacy Python tests before treating the
   repository-wide regression suite as green.

Until all relevant gates pass, the permanent-deletion gate stays closed and
human review is required before merge or any production use.
