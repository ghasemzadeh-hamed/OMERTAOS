# Gate S2 report — Core Service Migration

Original execution: 2026-07-12

Reconciled: 2026-08-10 on branch `CAPO`

Status: **passed on current locked CI evidence**

## R3 reconciliation

The registry outage below is retained as historical evidence. It was superseded
at commit `91921367cdfa600abb91710f7d699a183af800fa` by CI run
[`31358631289`](https://github.com/Hamedghz/OMERTAOS/actions/runs/31358631289):
the `test` job passed `cargo test --locked --all-targets` and
`cargo build --locked --release`, while `service-builds` passed the four
canonical service builds. `runtime-daemon/Cargo.lock` is tracked with SHA-256
`9C7EBC387FEF54CB7C2BBC70F96EA2DDF690F7636D18175FA251B96D5D5433F6`.

Gate S2 is therefore closed for repository compilation and tests. Native Linux
sandbox and service-lifecycle acceptance remain separate Native gates.

## Historical execution

## Retry history

### Retry 1 — 2026-07-12

The operator-approved Gate retry started from clean commit `653306bf`. Running
`cargo test --manifest-path runtime-daemon/Cargo.toml --all-targets` with bounded
network timeout/retries again failed to connect to `index.crates.io:443` for
multiple dependency requests. Compilation did not start, no test binary was
created, and the process was stopped after the repeated external-network failure.

Because the first unmet Gate condition was unchanged and no source changed, the
already-passing Control, Gateway and Console builds were not repeated in this
retry. The Gate remains not passed; this retry is not evidence of a Runtime
source failure.

## Gate requirement

All four canonical services must build:

1. Console
2. Gateway
3. Control
4. Runtime Daemon

Three services passed. Runtime Daemon could not begin compilation because the
Cargo registry was unreachable; therefore Gate S2 is not accepted and S3 should
not be treated as authorized by this result.

## Service results

| Service | Command / evidence | Result |
|---|---|---|
| Control | `python -m compileall -q control` and canonical app/client/orchestration imports | Passed |
| Gateway | `npm run build --prefix gateway` (`tsc`) | Passed |
| Console | `npm run build --prefix console` (`next build`) | Passed; 70 static pages generated |
| Runtime Daemon | `cargo test --manifest-path runtime-daemon/Cargo.toml --all-targets` | Blocked before compile: could not reach `index.crates.io:443` |

Runtime Cargo format and no-dependency metadata both passed. They validate
manifest/source structure but do not substitute for compilation or tests.

## Regression and configuration

- `tests/architecture tests/control`: 52 passed, 1 expected failure, 2 existing
  deprecation warnings. The failure is the intentionally red Structure
  completion gate while protected legacy roots and Console bypasses remain.
- Immediate canonical boundary invariants: 4 passed.
- Root, Quickstart and Local Compose configuration rendering: passed.
- Root Compose warned that `AION_VAULT_TOKEN` was unset and defaulted to blank;
  no stack was started and no secret was written.
- Git diff validation: no source deletion or database operation occurred.

## Console warnings

The production build exited zero but reported existing environment/dependency
warnings:

- Prisma client was not generated and `DATABASE_URL` was absent in the local
  build environment, so database client initialization was skipped;
- Browserslist/baseline mapping data is stale;
- `/api/claude/status` uses request headers and is rendered dynamically.

The build produced local `console/.next/` output. The repository now ignores
`**/.next/`; the generated directory was not deleted or committed.

## Required retry

On a host with crates.io access or a reviewed dependency mirror/cache, run:

```powershell
cargo test --manifest-path runtime-daemon/Cargo.toml --all-targets
cargo build --release --manifest-path runtime-daemon/Cargo.toml
```

Then rerun the architecture/Control tests and three Compose configuration checks.
Gate S2 passes only when both Runtime commands exit zero and no additional
regression appears. Native Linux sandbox acceptance remains a later mandatory
production gate even after compilation succeeds.

## Rollback

This Gate run changed no application behavior. Revert the Gate report commit to
remove only documentation and the generated-output ignore rule. Preserve source,
configuration and persistent state; no database rollback is needed.
