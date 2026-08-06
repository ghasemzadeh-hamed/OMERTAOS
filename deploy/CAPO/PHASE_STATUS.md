# CAPO phase status

> Historical phase ledger: phase-specific limitations below describe their
> original execution dates. The current N1-N8 contract supersedes old claims
> that Gateway/Runtime lack lockfiles or that rollback disables the target.
> Current rollback verifies and atomically switches immutable releases; live
> Linux acceptance still requires a fresh recorded run.

This file is the durable state machine for the seven-run CAPO automation. A phase
is attempted exactly once and is recorded as `complete`, `failed`, or `blocked`.

## Baseline

- Branch: `capo`
- Baseline commit: `b4021a4327d63b8db0c0e0f87267dec28907cb36`
- Backup: `D:\GHASEMZADEH\P\OMERTAOS-backups\capo\20260711-161030`
- Backup scope: complete Git history/refs, tracked-source archive, expanded tracked
  snapshot, and the source Executive Summary document
- Excluded by design: secrets, databases, Docker volumes, dependency/build caches
- Permanent deletion gate: closed until Native and Quickstart acceptance both pass

## Phase 1 — Repository audit and baseline

- Status: complete
- Started: 2026-07-11 16:17 Asia/Tehran
- Finished: 2026-07-11 16:20 Asia/Tehran
- Backup verification:
  - repository bundle SHA-256: `1B540FEFA81ED19B50F3973D9FEA9CC81C0D26D20BC8BFF2BEFEBE298ED8A30C`
  - tracked source SHA-256: `0C6D9145CEE2B576AB74FA7770739DB718D660C20C39B501F2A637D8DB80E41A`
  - source brief SHA-256: `BF2B13C80F1AA1171BF8CCA91130AD18E00CBA324161BDFF1A19B68721DAF844`
  - `git bundle verify`: passed; full history recorded
  - restore clone: passed; restored HEAD matched the baseline commit
- Changed files:
  - `deploy/CAPO/PHASE_STATUS.md`
  - `docs/capo/repository-audit.md`
  - `docs/capo/reconstruction-map.md`
- Database objects: none
- API/UI impact: none
- Permission/security impact: none
- Native status: design/static audit only; runtime acceptance pending on Linux SSD
- Quickstart status: configuration contract retained; targeted validation recorded below
- Validation:
  - backup SHA-256 verification: passed for all three recorded artifacts
  - isolated Git bundle restore: passed at the baseline commit
  - `docker compose -f docker-compose.quickstart.yml config --quiet`: passed
  - `docker compose -f docker-compose.local.yml config --quiet`: passed
  - `python -m pytest tests/architecture -q`: `14 passed in 0.70s`
  - `git diff --check`: passed
- Coverage: not generated; Phase 1 changes only documentation and status records
- Risk: low (documentation and recovery metadata only)
- Migration: none; no path moved or removed
- Rollback: revert the phase commit; external verified backup remains unchanged
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Next phase: CAPO contract and scaffold

## Remaining phases

| Phase | Name | Status |
|---:|---|---|
| 2 | CAPO contract and scaffold | complete |
| 3 | Native OS and data installers | complete |
| 4 | Application installers and selective reconstruction | complete |
| 5 | Native service lifecycle | complete |
| 6 | Dual-path validation and recovery | complete |
| 7 | Final review and handoff | complete |

## Phase 2 — CAPO contract and scaffold

- Status: complete
- Started: 2026-07-11 21:09 Asia/Tehran
- Finished: 2026-07-11 21:09 Asia/Tehran
- Changed files:
  - `deploy/CAPO/README.md`
  - `deploy/CAPO/CAPO.env.example`
  - `deploy/CAPO/scripts/README.md`
  - `deploy/CAPO/systemd/README.md`
  - `deploy/CAPO/tests/README.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: none
- API/UI impact: none; canonical ports and flow are documented only
- Permission/security impact: documents a future dedicated non-root `omertaos`
  account; no permission or auth implementation changed
- Validation:
  - Phase 2 PowerShell contract assertions: passed after making the three
    optional-service flag names explicit in the README
  - `python -m pytest tests/architecture -q`: `14 passed in 0.75s`
  - `git diff --check`: passed (Git reported only the existing Windows checkout
    LF-to-CRLF warning for this status file)
- Coverage: not generated; Phase 2 changes configuration examples and Markdown
- Risk: low (additive deployment contract and non-secret example only)
- Security: placeholder secrets only; optional stores default disabled; no native
  commands executed on Windows
- Migration: none; no existing path, data, service, or configuration moved
- Rollback: revert the single Phase 2 commit; runtime behavior is unchanged
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Limitations: native Linux/systemd behavior is intentionally unverified until
  later phases and a provided Linux SSD host
- Next phase: native OS and data installers

## Phase 3 — Native OS and data installers

- Status: complete
- Started: 2026-07-12 00:01 Asia/Tehran
- Finished: 2026-07-12 00:04 Asia/Tehran
- Changed files:
  - `deploy/CAPO/scripts/install-os-packages.sh`
  - `deploy/CAPO/scripts/install-data-services.sh`
  - `deploy/CAPO/scripts/README.md`
  - `deploy/CAPO/CAPO.env.example`
  - `deploy/CAPO/README.md`
  - `docs/capo/native-os-data-installers.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: on a future Linux execution, one configured PostgreSQL login
  role and database are created only when absent; this Windows run created none
- API/UI impact: none
- Permission/security impact: the OS installer can create the dedicated non-root
  `omertaos` account and restricted state/configuration directories on Linux;
  application auth and permissions are unchanged
- Validation:
  - Phase 3 PowerShell static contract assertions: passed (the first invocation
    had an over-escaped test literal; the corrected unchanged assertion passed)
  - `python -m pytest tests/architecture -q`: `14 passed in 0.67s`
  - `git diff --check`: passed (Git reported only expected Windows checkout
    LF-to-CRLF warnings for tracked text files)
  - local Bash/shellcheck validation: skipped; WSL Bash was unavailable and no
    pre-existing Docker Bash image was available; no package/image was installed
- Coverage: not generated; application runtime code was not changed
- Risk: medium (reviewed scripts perform package, account, service, and database
  setup when explicitly executed on a supported Linux host)
- Security: dry-run/help and OS checks included; PostgreSQL identifiers are
  restricted and values use psql quoting; existing role passwords/data are
  preserved; optional stores default disabled; no real secrets stored
- Migration: no application schema migration or seeding; existing PostgreSQL
  objects are preserved and database-owner mismatch fails for review
- Rollback: stop/disable native PostgreSQL and Redis if appropriate; revert the
  phase commit; do not delete created accounts, directories, roles, databases,
  or data without separate backup evidence and explicit approval
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Limitations: installers were statically reviewed only on Windows; native
  Debian/Ubuntu execution and systemd/database acceptance remain pending on the
  intended Linux SSD host
- Next phase: application installers

## Phase 4 — Application installers

- Status: complete
- Started: 2026-07-12 02:05 Asia/Tehran
- Finished: 2026-07-12 02:11 Asia/Tehran
- Changed files:
  - `deploy/CAPO/scripts/install-python-control.sh`
  - `deploy/CAPO/scripts/install-node-services.sh`
  - `deploy/CAPO/scripts/install-rust-runtime.sh`
  - `deploy/CAPO/scripts/README.md`
  - `deploy/CAPO/README.md`
  - `docs/capo/application-installers.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: none; installers do not perform schema operations
- API/UI impact: none; canonical build and entrypoint contracts are consumed
  without changing application sources or public behavior
- Permission/security impact: no auth or permission changes; scripts do not read
  or print secrets and do not start services
- Validation:
  - Git Bash `bash -n`, `--help`, and Phase 4 static safety assertions: passed
    for all three installers
  - `python -c` import of `control.app.main:app`: passed
  - `npm run build --prefix gateway`: passed
  - `npm run build --prefix console`: passed with existing warnings about an
    ungenerated Prisma client, missing database URL, stale browser mapping data,
    and a dynamic server route; Next completed all 70 static pages
  - `cargo metadata --manifest-path runtime-daemon/Cargo.toml --no-deps
    --format-version 1`: passed
  - `cargo build --manifest-path runtime-daemon/Cargo.toml --release`: blocked
    by repeated inability to connect to `index.crates.io:443`; stopped after
    retries rather than changing network or installing dependencies
  - `python -m pytest tests/architecture -q`: `14 passed in 0.64s`
  - `git diff --check`: passed with expected Windows LF-to-CRLF warnings
- Coverage: not generated; Phase 4 changes deployment scripts/documentation and
  does not change application runtime code
- Risk: medium (scripts install/build native application artifacts when an
  operator executes them on Linux)
- Security: dedicated paths and canonical entrypoints retained; no secrets,
  service starts, unsupported Runtime flags, destructive commands, or blanket
  `|| true` were introduced
- Migration: additive installers only; no source, data, API, schema, legacy path,
  or Docker Quickstart migration
- Rollback: revert the single Phase 4 commit and rebuild generated application
  artifacts from the prior commit; preserve persistent data and configuration
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Limitations: Gateway and Runtime currently have no committed lockfiles; Gateway
  reports and uses `npm install`, while Runtime uses locked Cargo mode only if a
  lockfile exists. Native Linux and full Runtime build verification remain
  pending on the intended Linux SSD host with registry access.
- Next phase: native service lifecycle

## Phase 5 — Native service lifecycle

- Status: complete
- Started: 2026-07-12 07:09 Asia/Tehran
- Finished: 2026-07-12 07:13 Asia/Tehran
- Changed files:
  - `deploy/CAPO/systemd/omertaos-{runtime,control,gateway,console}.service`
  - `deploy/CAPO/systemd/omertaos.target`
  - `deploy/CAPO/scripts/{setup-systemd,first-boot,run-all,stop-all}.sh`
  - `deploy/CAPO/systemd/README.md`
  - `deploy/CAPO/scripts/README.md`
  - `deploy/CAPO/README.md`
  - `docs/capo/service-lifecycle.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: none; units consume the existing PostgreSQL and Redis
  services without changing schemas, roles, databases, or persistent data
- API/UI impact: none; canonical commands and ports are consumed without
  changing application sources or public behavior
- Permission/security impact: services run as the existing non-root `omertaos`
  account with `NoNewPrivileges`, private temporary directories, and the
  operator-owned `/etc/omertaos/omertaos.env`; application auth is unchanged
- Validation:
  - Git Bash `bash -n` and `--help`: passed for all four lifecycle scripts
  - Phase 5 PowerShell static assertions: passed for five systemd assets,
    lifecycle commands, canonical ports, ordering, restart bounds, Runtime CLI
    safety, and forbidden destructive commands
  - initial syntax-test launcher selected the broken Windows WSL Bash shim and
    failed before reading a script; rerun explicitly with Git Bash passed
  - `python -m pytest tests/architecture -q`: `14 passed in 0.64s`
  - `git diff --check`: passed with expected Windows LF-to-CRLF warnings
- Coverage: not generated; Phase 5 changes deployment assets and documentation,
  not application runtime code
- Risk: medium (reviewed units and scripts control native Linux service
  lifecycle when explicitly installed and run by an operator)
- Security: no real secrets, destructive commands, unsupported Runtime flags,
  blanket `|| true`, auth changes, or root application services were added;
  configuration remains outside Git
- Migration: additive native service definitions only; no source, data, schema,
  public API, legacy path, or Docker Quickstart migration
- Rollback: stop and disable `omertaos.target`, restore prior unit definitions if
  any, run `systemctl daemon-reload`, and revert this phase commit; preserve the
  environment file, account, database, and persistent state
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Limitations: systemd and native Linux path/ownership behavior were statically
  reviewed only and remain pending on the intended Linux SSD host
- Next phase: dual-path validation and recovery

## Phase 6 — Dual-path validation and recovery

- Status: complete
- Started: 2026-07-12 09:36 Asia/Tehran
- Finished: 2026-07-12 09:42 Asia/Tehran
- Changed files:
  - `deploy/CAPO/scripts/smoke-test.sh`
  - `deploy/CAPO/scripts/rollback.sh`
  - `deploy/CAPO/tests/contract-tests.ps1`
  - `deploy/CAPO/{README.md,scripts/README.md,tests/README.md}`
  - `docs/capo/validation-recovery.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: none; validation and rollback do not modify databases or
  persistent data
- API/UI impact: none; existing health endpoints and canonical ports are only
  consumed by read-only checks
- Permission/security impact: no application permission changes; rollback may
  stop/disable only the aggregate CAPO systemd target on an explicitly selected
  Linux host and preserves configuration, accounts, source, and state
- Validation:
  - Git Bash `bash -n` and `--help`: passed for smoke and rollback scripts
  - Phase 6 PowerShell contract tests: passed for environment keys, ports,
    systemd hardening, rollback preservation, and forbidden commands
  - both Quickstart and Local Compose configuration rendering: passed
  - `python -m pytest tests/architecture -q`: `14 passed in 0.65s`
  - `git diff --check`: passed with expected Windows LF-to-CRLF warnings
  - running Quickstart smoke: skipped because the local Docker daemon did not
    respond; the stack was not started or mutated
  - Native smoke: pending on the intended Debian/Ubuntu SSD systemd host
- Coverage: not generated; application runtime code was not changed
- Risk: medium (read-only probes and an operator-invoked native lifecycle
  rollback script were added)
- Security: no secret values, destructive commands, data deletion, auth bypass,
  unsupported Runtime flags, or Docker dependency in Native readiness added
- Migration: none; Native and Quickstart remain independent and all legacy
  recovery inputs remain in place
- Rollback: run `rollback.sh --dry-run`, then `rollback.sh` if approved; revert
  the Phase 6 commit separately and preserve all persistent volumes/state
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Limitations: configuration/static validation is complete, but native Linux
  and running Quickstart acceptance remain explicitly pending; permanent path
  retirement remains blocked
- Next phase: final review, acceptance report, and PR-ready handoff

## Phase 7 — Final review and handoff

- Status: complete
- Started: 2026-07-12 09:45 Asia/Tehran
- Finished: 2026-07-12 10:00 Asia/Tehran
- Changed files:
  - `docs/capo/acceptance-report.md`
  - `docs/capo/PR_DESCRIPTION.md`
  - `deploy/CAPO/README.md`
  - `deploy/CAPO/PHASE_STATUS.md`
- Database objects: none
- API/UI impact: none; final review and handoff documentation only
- Permission/security impact: none; existing CAPO security controls were
  reviewed and recorded without changing application authorization
- Validation:
  - backup SHA-256 and complete Git bundle verification: passed
  - Bash syntax/help and Phase 6 CAPO contracts: passed
  - Quickstart and Local Compose configuration rendering: passed
  - `python -m pytest tests/architecture -q`: `14 passed in 0.95s`
  - Control import, Gateway build, Console production build, and Runtime Cargo
    metadata: passed; Console retained documented local warnings
  - Runtime release build: blocked by inability to reach `index.crates.io:443`
  - full Python regression: blocked during collection by 11 legacy imports for
    removed `os.control`, `os.kernel`, `aion`, and CLI paths
  - Native smoke: pending on the intended Linux SSD host
  - running Quickstart smoke: pending because the Docker daemon did not respond
- Coverage: not generated; no application runtime code changed
- Risk: low for Phase 7; overall CAPO operator scripts remain medium risk and
  require human review before Linux or production execution
- Security: no secrets, destructive commands, data deletion, auth changes,
  public API changes, merge, push, or deployment
- Migration: none; all changes remain additive
- Rollback: revert the Phase 7 commit to remove only the final handoff records;
  use the documented non-destructive CAPO rollback for native service lifecycle
- Commit: the commit containing this phase record; resolve with
  `git log -1 -- deploy/CAPO/PHASE_STATUS.md`
- Acceptance: conditional for human review only; Native and running Quickstart
  gates remain pending and permanent legacy-path retirement remains blocked
- Automation: all seven phases attempted; no further CAPO phase is scheduled by
  this ledger
