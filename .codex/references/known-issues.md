# OMERTAOS Known Issues

## Active Issues

| ID | Area | Issue | Severity | Status |
|---|---|---|---|---|
| 009 | Bridge | Windows Agentic Bridge compatibility paths still require their task-scoped S3 migration and validation | P2 | Open |
| 010 | Runtime | Full Cargo build/test remains dependent on reachable crates.io or a prepared offline cache | P1 | Blocked externally |
| 011 | Python | Full regression collection still contains legacy import assumptions; use targeted suites until repaired in scope | P1 | Open |

## Fixed Issues

| ID | Area | Fix | Date |
|---|---|---|---|
| 001 | Docker | `control/Dockerfile` exists; validate it when Control packaging changes | 2026-07-13 |
| 002 | Docker | `gateway/Dockerfile` exists; validate it when Gateway packaging changes | 2026-07-13 |
| 003 | Docker | Local Compose disables the optional development kernel instead of requiring a missing root | 2026-07-13 |
| 004 | Control | `control/` is canonical and `control-plane/` is compatibility-only under the ownership ADR | 2026-07-12 |
| 005 | Runtime | `runtime-daemon/` is canonical and `rust-runtime/` delegates as a compatibility crate | 2026-07-12 |
| 006 | Data | Implementations were consolidated under `data/`; legacy roots remain compatibility inputs | 2026-07-12 |
| 007 | Models | Metadata is canonical in `registry/models/`; provider/client behavior was split to owned layers | 2026-07-12 |
| 008 | Schemas | Authored contracts are canonical under `schemas/v1/`; generated bindings use `shared/generated/` | 2026-07-13 |
