# CAPO phase status

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
| 4 | Application installers and selective reconstruction | pending |
| 5 | Native service lifecycle | pending |
| 6 | Dual-path validation and recovery | pending |
| 7 | Final review and handoff | pending |

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
