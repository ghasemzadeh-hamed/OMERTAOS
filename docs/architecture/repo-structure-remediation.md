# Repository Structure Remediation (Phase Plan)

This document addresses current structure drift and duplicated roots reported in the repository.

## Canonical policy

- Keep runtime and product code under canonical roots from `STRUCTURE.md`.
- Keep deployment artifacts under `deploy/*`.
- Keep compatibility wrappers only when migration is still in progress.

## Drift list and planned destination

| Current path | Issue | Target state |
|---|---|---|
| `/v1` | legacy API root | move handlers/specs under `control/` or `gateway/`, keep `/v1` as route prefix only |
| `/worker` | top-level worker root | move worker implementations into `execution/` or `control/` by ownership |
| `/ui` | duplicated frontend root beside `console/` | keep one canonical frontend root (`console/`) and move shared assets to `shared/` |
| `/protos` | stand-alone schema root | keep protobuf as schema assets under `schemas/` (with compatibility path until migration done) |
| `/process-analytics` | naming + placement drift | migrate to `bigdata/process_analytics` |
| `/llm` | root-level functional island | place runtime logic in `registry/` or `execution/` and configs in `config/` |
| `/config` + `/configs` | duplicate config roots | `config/` for runtime config, `configs/` deprecated or moved to `deploy/` |
| `/models` + `/control/models` | model metadata duplication | choose source of truth (`registry/models` preferred) + wrappers |
| `/ci` + `/deploy/ci` | duplicate CI roots | keep `deploy/ci` canonical |
| `/core/systemd` + `/deploy/systemd` | duplicate unit roots | keep `deploy/systemd` canonical |
| `/scripts` + `/deploy/scripts` | unclear script boundary | `scripts/` dev tooling, `deploy/scripts` ops scripts |
| `/kernel/profiles` | incomplete + undocumented | add profile index + completion matrix |

## Immediate guardrail

Run:

```bash
python3 tools/repo_audit/check_structure_consistency.py
```

- Exit code `1` means at least one blocking structure issue (`ERROR`) exists.
- `WARN`/`INFO` findings are migration-tracking items.

## Migration sequencing

1. **Inventory and ownership:** assign owner for each drift path.
2. **Dual-write period:** introduce wrappers/symlinks/import aliases where needed.
3. **Reference rewrite:** update docs, CI, and scripts to canonical paths.
4. **Removal:** remove legacy roots after two stable release cycles.
