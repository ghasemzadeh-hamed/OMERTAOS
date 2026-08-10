# OMERTAOS Known Issues

## Active Issues

No Structure/S3 migration issue is currently open. Native, Docker and feature
readiness remain subject to their own current acceptance evidence.

## Fixed Issues

| ID | Area | Fix | Date |
|---|---|---|---|
| 001 | Docker | `control/Dockerfile` exists; validate it when Control packaging changes | 2026-07-13 |
| 002 | Docker | `gateway/Dockerfile` exists; validate it when Gateway packaging changes | 2026-07-13 |
| 003 | Docker | Local Compose disables the optional development kernel instead of requiring a missing root | 2026-07-13 |
| 004 | Control | `control/` is canonical and retired migration owners are absent | 2026-08-10 |
| 005 | Runtime | `runtime-daemon/` is canonical and retired migration owners are absent | 2026-08-10 |
| 006 | Data | Implementations are consolidated under `data/`; retired roots are absent | 2026-08-10 |
| 007 | Models | Metadata is canonical in `registry/models/`; provider/client behavior was split to owned layers | 2026-07-12 |
| 008 | Schemas | Authored contracts are canonical under `schemas/v1/`; generated bindings use `shared/generated/` | 2026-07-13 |
| 009 | Bridge | The canonical Bridge owns its active entrypoint and validation contracts | 2026-08-10 |
| 010 | Runtime | Locked Cargo test/build completed in the R1 baseline and CI | 2026-08-09 |
| 011 | Python | Architecture guards distinguish runtime dependencies from historical evidence | 2026-08-10 |
