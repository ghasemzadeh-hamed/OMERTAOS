# ADR 0001: Canonical AION service ownership

- Status: accepted
- Date: 2026-07-05

## Context

The repository contains competing generations: `control/` and `control-plane/`,
`runtime-daemon/` and `rust-runtime/`, `data/`, `database/` and `db/`, plus model,
schema and deployment duplicates. Earlier documentation also disagrees about which
generation is primary. A previous cleanup removed the former `control.os`
implementation while leaving its callers and wrappers behind.

## Decision

The canonical execution chain is `console -> gateway -> control -> runtime-daemon`.
Canonical supporting owners are `data/`, `registry/`, `policies/`, `schemas/`,
`shared/`, `deploy/`, and `integrations/`. Legacy roots are migration inputs and
compatibility surfaces only. New feature behavior must not be added to them.

The Python "kernel" is not restored as a privileged executor. Its useful tenant,
scheduling and governance concepts move into Control; all host side effects stay in
the Rust Runtime Daemon.

## Consequences

- Deleted capabilities are recovered selectively into canonical modules.
- Existing public APIs remain stable through Gateway adapters during migration.
- Compatibility imports point toward canonical code.
- Cleanup is delayed until callers and deployment references are zero.
- CI architecture tests must inspect canonical paths, not legacy ones.

## Rollback

This is a documentation and ownership decision. Reverting it requires a new ADR,
an explicit service migration plan, compatibility tests and human approval; it must
not be reversed by moving individual files ad hoc.

