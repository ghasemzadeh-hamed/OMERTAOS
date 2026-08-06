# S5 final legacy retirement

Date: 2026-07-15

Branch: `capo-structure`

Status: **implementation completed with explicit operator deletion approval; Runtime acceptance remains blocked by registry access**

## Retired inputs

S5 removed the migration-era Control, orchestration, Runtime, Data, model,
schema/UI alias, Event Bus, observability, Agent, Windows Bridge and deployment
mirror roots after their canonical counterparts and callers were verified. The
legacy deployment paths required by Gate S4 are now absent, including
`execution/`, `docker/`, `infra/`, `core/systemd/` and `scripts/deploy/`.

The older deployment aliases inside `deploy/` were also retired after canonical
ownership was established under `deploy/native/`, `deploy/docker/` and
`deploy/kubernetes/`. The unique edge setup script was preserved as
`deploy/native/scripts/aion-edge-setup.sh`.

## Boundary correction

The Console endpoint helper now sends both Gateway- and Control-labelled
capability calls through the Gateway public endpoint. System health preserves
its existing response fields but derives Control status from the Gateway health
dependency response rather than connecting to Control directly.

## Validation

- Gate S4 legacy-path check: passed; all five forbidden paths are absent.
- Architecture tests including the final Structure gate: 60 passed.
- Architecture, Control and Data tests: 97 passed with two existing warnings.
- Gateway TypeScript build: passed.
- Console Vitest: 5 files and 8 tests passed; production build passed.
- Windows Bridge Server build and 3 tests: passed; Bridge UI build passed.
- Canonical Quickstart, Local and Full Compose rendering: passed.
- Runtime formatting and no-dependency metadata: passed.
- Runtime tests: blocked because crates.io was unreachable and the local cache
  lacks `anyhow`; no Runtime test success is claimed.

No stack, installer, systemd unit or deployment was started. Linux/systemd and
live Native/Quickstart acceptance remain pending.

## Rollback

Revert the S5 change set to restore retired paths from Git, then revert S4 if
the old deployment entrypoints are also required. Do not modify persistent data
or external services as part of source rollback.
