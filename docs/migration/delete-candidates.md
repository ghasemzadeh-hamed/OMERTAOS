# Delete candidates — Structure S0

Date: 2026-07-12

Status: candidates only; no deletion is authorized by this document.

## Immediate artifact candidates

| Path | State | Evidence still required |
|---|---|---|
| `registry/__init__.py.rej` | `DELETE` candidate | Inspect rejected patch and Git history; confirm no unapplied change is needed |
| `migration/logs/console-build.log` | `GENERATED` / `DELETE` candidate | Confirm no audit process consumes tracked build logs; add ignore rule if needed |
| `pr_commit_plan.json` | `DELETE` candidate | Inspect history and automation references |

## Legacy-root candidates after migration

The following are not current deletion candidates at file level. Their roots may
be retired only after the named migration and acceptance gates pass.

| Root | Prerequisite owner/gate |
|---|---|
| `control-plane/`, `orchestration/` | S2 Control merge, imports/tests/builds pass |
| `rust-runtime/` and Runtime portions of `execution/` | S2 Runtime merge and Cargo acceptance pass |
| `database/`, `db/` | S3 data adapter/interface migration passes |
| `models/` | S3 registry/provider/client split passes |
| root `protos` symlink and duplicate schema paths | Versioned schema/generated-client tests pass |
| `eventbus/`, `observability/` | Contracts, ports, integrations and deployment assets are split and tested |
| `execution/windows-agentic-bridge/` | Full-tree diff and integration build/tests pass |
| root `docker/`, `infra/`, deployment content in `execution/` | S4 Native and Quickstart parity pass |
| root `ui` symlink | Console/UI-core references and builds pass |

## Unknown and therefore protected

`algorithms/`, `cluster/`, `desktop-shell/`, `domain/`, the `process-analytics`
symlink, and any unique file found during a directory diff are protected as
`UNKNOWN`. They cannot be deleted until ownership, consumers, history and a
canonical destination are documented.

## Permanent deletion gate

Deletion remains closed unless all conditions are met:

- verified backup/tag and Git history remain recoverable;
- canonical destination contains every required unique/newer file;
- imports, CI, schemas, deploy assets and documentation references are updated;
- architecture, module, Native and Docker/Quickstart tests pass;
- `rg` checks have no unexplained executable legacy references;
- a human reviews and explicitly approves the S5 deletion set.

S0 performed no `rm`, `Remove-Item`, `git rm`, `DROP` or `TRUNCATE` operation.
