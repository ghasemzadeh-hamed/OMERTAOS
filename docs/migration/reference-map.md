# Legacy reference map — Structure S0

Date: 2026-07-12

Method: focused `rg` scans excluding `.git`, dependency and build-cache trees.

Counts below are files containing the literal path token. Documentation and
migration history are evidence and may remain after runtime references reach
zero; each later phase must distinguish executable references from historical
mentions.

| Token | Files | Runtime/config hotspots | Canonical target |
|---|---:|---|---|
| `control-plane` | 14 | `.env.example`, `control/app/__init__.py`, architecture test, cleanup script | `control/` |
| `rust-runtime` | 18 | CI, CAPO installer/lifecycle scripts, legacy Cargo sources | `runtime-daemon/` |
| `database/` | 9 | No application hit in this literal scan; docs dominate | `data/` |
| `db/` | 12 | Compose catalogs and JS lockfiles include this token | `data/` after contextual review |
| `models/` | 21 | Console pages, compose examples, both model trees | `registry/models/` plus provider/control owners |
| `protos/` | 3 | `gateway/src/grpcClient.ts`, `gateway/src/server/grpc.ts`, `STRUCTURE.md` | `schemas/v1/protos/` |
| `execution/` | 6 | Documentation references in the literal scan | Split by canonical owner |

## High-priority dependency edges

| Source | Current dependency | Required S2/S3 action |
|---|---|---|
| `.env.example` | `control-plane` path | Change only after Control migration contract exists |
| `control/app/__init__.py` | compatibility reference to `control-plane` | Remove compatibility dependency after merge and tests |
| `.github/workflows/ci.yml` | `rust-runtime` | Add canonical Runtime validation before retiring legacy job |
| `deploy/CAPO/scripts/install-rust-runtime.sh` | legacy detection/fallback | Preserve recovery until canonical Runtime acceptance passes |
| `gateway/src/grpcClient.ts` | proto path | Switch to generated client contract, not a private proto copy |
| `gateway/src/server/grpc.ts` | proto path | Same versioned schema/generated-client migration |
| `docker/compose.catalog.yml` | `db/` token | Compare with canonical deploy catalog before consolidation |
| `execution/compose.catalog.yml` | `db/` token | Merge into `deploy/` and update data ownership references |
| Console model pages | model URL/path concepts | Verify API semantics; do not treat UI route names as imports |

## Reference update gates

1. A canonical implementation and versioned contract must exist first.
2. Update application, build, CI, deploy and test references together.
3. Documentation/history mentions may remain when explicitly labeled legacy.
4. A zero-result search alone is not proof: builds, architecture tests and both
   deployment modes must still pass.
