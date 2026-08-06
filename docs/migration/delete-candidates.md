# Delete candidates — Structure S0

Date: 2026-07-12

Status: candidates only; no deletion is authorized by this document.

## Immediate artifact candidates

| Path | State | Evidence still required |
|---|---|---|
| `registry/__init__.py.rej` | `RESOLVED S6` | Rejected hunk was obsolete legacy registry code; preserved under migration evidence and `*.rej` is ignored |
| `migration/logs/console-build.log` | `RESOLVED S6` | Preserved under `docs/migration/evidence/`; generated logs are ignored |
| `pr_commit_plan.json` | `RESOLVED S6` | No automation consumer found; preserved under migration evidence |

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

## Former unknown roots resolved in S6

S6 resolved ownership without discarding file contents: Desktop Shell moved to
the Console owner, Native profiles moved under `deploy/native/`, Cluster
headings moved to architecture documentation, and inactive placeholders,
duplicate domain code and broken links moved under migration evidence. The
verified external backup and Git bundle retain complete recovery history.

## Permanent deletion gate

Deletion remains closed unless all conditions are met:

- verified backup/tag and Git history remain recoverable;
- canonical destination contains every required unique/newer file;
- imports, CI, schemas, deploy assets and documentation references are updated;
- architecture, module, Native and Docker/Quickstart tests pass;
- `rg` checks have no unexplained executable legacy references;
- a human reviews and explicitly approves the S5 deletion set.

S0 performed no `rm`, `Remove-Item`, `git rm`, `DROP` or `TRUNCATE` operation.
