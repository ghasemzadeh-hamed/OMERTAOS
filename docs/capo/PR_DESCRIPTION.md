# feat(capo): add native deployment, validation, and recovery profile

> Historical draft: refresh all check counts and Runtime results before use.
> Current N8 uses committed Gateway/Runtime lockfiles, verified external backup
> manifests, immutable releases, and atomic rollback rather than target disable.

## Summary

Adds the seven-phase CAPO deployment profile for Debian/Ubuntu while preserving
the existing Docker Quickstart and canonical Console → Gateway → Control →
Runtime flow. The change is additive, backup-first, and does not delete or move
legacy paths, schemas, tables, or data.

## Why

OMERTAOS needs a reviewable Native Linux installation path with explicit
service ownership, repeatable setup, health validation, troubleshooting, and a
non-destructive recovery procedure without replacing Quickstart.

## Changed areas

- `deploy/CAPO/`: environment contract, installers, systemd units, lifecycle,
  smoke/rollback scripts, contract tests, and phase ledger.
- `docs/capo/`: repository audit, reconstruction map, installer/service guides,
  validation/recovery guide, and acceptance report.

## Validation

- [x] Verified external backup hashes and complete Git bundle
- [x] CAPO Bash syntax/help checks
- [x] CAPO contract tests
- [x] Quickstart and Local Compose configuration rendering
- [x] Architecture tests: 14 passed
- [x] Control import and Gateway build
- [x] Console production build, with documented local Prisma/browser-data warnings
- [x] Runtime Cargo metadata
- [ ] Runtime locked tests and release build on the target toolchain
- [ ] Native Debian/Ubuntu SSD smoke and reboot acceptance
- [ ] Running Docker Quickstart smoke; local daemon was unavailable
- [ ] Full Python regression; legacy removed-path imports fail collection

Coverage was not generated because application runtime code was not changed.

## Risk and security

Risk is medium: scripts can install packages, create a dedicated account and
database role, build applications, and control systemd when explicitly run on
Linux. Scripts include state checks, help/dry-run paths where mutating, bounded
service restart behavior, non-root application units, external secret storage,
and no destructive cleanup.

## Migration and rollback

There is no public API migration. Native and Quickstart remain independent.
Roll back by verifying and previewing `deploy/CAPO/scripts/rollback.sh`, then
atomically selecting the prior immutable release. Preserve `/etc/omertaos`,
`/var/lib/omertaos`, databases, volumes, and the verified external backup;
database downgrade is never automatic.

## Review checklist

- [ ] Human review of package/database/systemd commands
- [ ] Security review of production secrets and network exposure
- [ ] Execute both Native and Quickstart acceptance gates
- [ ] Confirm no permanent legacy-path retirement
- [ ] Do not merge or deploy until pending checks are dispositioned
