# Repository Refactor Plan

## Goals

- Keep `docker-compose.quickstart.yml` buildable while the repository is normalized.
- Preserve public API behavior and import compatibility during the transition.
- Move code only after history, ownership, and runtime references are understood.

## Canonical Structure

- `control/` is the canonical Python control plane.
- `runtime-daemon/` is the canonical Rust runtime.
- `data/` is the canonical data layer.
- `registry/models/` is the canonical model registry.
- `registry/agents/` is the canonical agent registry.
- `deploy/` is the canonical deployment and infrastructure folder.
- `schemas/protos` remains the active protobuf tree until generated-code consumers are reconciled.

## Phase 1: Quickstart Stabilization

- Keep the quickstart compose file self-contained with local defaults.
- Ensure only `control`, `gateway`, and `console` need to build from local Dockerfiles.
- Keep health endpoints stable:
  - control HTTP: `8000`
  - gateway HTTP: `8080`
  - console HTTP: `3000`
  - runtime gRPC default: `50051`
- Add compatibility packages or wrappers for declared local dependencies when the target package is missing.

## Phase 2: Inventory and Dependency Map

- Generate a path inventory for duplicate roots:
  - `control/` and `control-plane/`
  - `runtime-daemon/` and `rust-runtime/`
  - `data/`, `database/`, and `db/`
  - `models/` and `registry/models/`
  - `agents/` and `registry/agents/`
  - `deploy/`, `execution/`, `infra/`, `docker/`, and `core/systemd/`
  - `schemas/protos` and `schemas/v1/protos`
- For each duplicate root, record:
  - imports and runtime references
  - Docker, CI, and script references
  - git history and recent ownership
  - generated files versus source files

## Phase 3: Compatibility Wrappers

- Add import wrappers before moving code when public paths are already referenced.
- Prefer forwarding modules, symlinks, or package-level shims over broad import rewrites.
- Mark wrappers with short comments that identify the canonical target and planned removal condition.

## Phase 4: Controlled Migration

- Migrate legacy `control-plane/` modules into `control/` only when they are still referenced or provide missing behavior.
- Migrate useful `rust-runtime/` assets into `runtime-daemon/`; archive unused historical files after history review.
- Consolidate data access into `data/`, preserving adapters for old `database/` and `db/` imports.
- Move model registry assets under `registry/models/`.
- Move agent registry assets under `registry/agents/`.
- Move deployment assets into `deploy/`, keeping thin pointers from old infra paths during one release window.

## Phase 5: Cleanup Gates

- Before deleting or archiving any root:
  - run `git log --oneline -- <path>`
  - inspect file type, symlink target, and current contents
  - search for references with `rg`
  - run compose config/build and relevant tests
- Remove wrappers only after no code, docs, CI, Dockerfiles, or scripts reference the old paths.

## Current Recommendations

- Do not delete `ui`; it is a compatibility symlink to `console/ui`.
- Do not delete `process-analytics` yet; it is a symlink to `bigdata/process_analytics`, but the target is absent in this checkout. Confirm whether the target was intentionally archived before removing or replacing it.
- Keep README and STRUCTURE updates tied to a successful Docker quickstart validation so the docs do not overstate runtime readiness.
