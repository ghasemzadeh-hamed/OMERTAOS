# CAPO repository audit

Audit date: 2026-07-11. Baseline: branch `capo` at
`b4021a4327d63b8db0c0e0f87267dec28907cb36`.

## Outcome

The supported architecture remains:

```text
Console :3000 -> Gateway :8080 -> Control :8000 -> Runtime :50051
                                      |
                      Data / Registry / Policies / Schemas
```

CAPO must add a native Debian/Ubuntu systemd deployment without weakening Docker
Quickstart. Existing legacy roots are recovery inputs, not active destinations.
No directory is safe to delete during this seven-phase workflow because Native
acceptance cannot be proven from the current Windows host.

## Backup gate

The external baseline contains a verified Git bundle with all refs/history, a ZIP
of all 851 tracked files at HEAD, an expanded tracked snapshot, and the source Word
brief. The bundle was cloned into a temporary directory and produced the exact
baseline HEAD. Checksums and restore instructions live with the backup.

Generated dependencies (`node_modules`, `.next`, `dist`, Rust `target`), local
secrets, databases, and Docker volumes are not source artifacts and are explicitly
outside this backup. Production data requires separate service-level backups.

## Canonical entrypoints

| Component | Canonical source | Build/start contract | Port |
|---|---|---|---:|
| Console | `console/` | `npm run build`, `npm run start` | 3000 |
| Gateway | `gateway/` | `npm run build`, `node dist/server.js` | 8080 |
| Control | `control/` | `uvicorn control.app.main:app` | 8000 |
| Runtime | `runtime-daemon/` | Cargo binary `runtime-daemon`; bind via `AION_RUNTIME_BIND_ADDR` | 50051 |

The current historical systemd files are not suitable CAPO templates: they use
old `/opt/aion` paths, removed `os.control.main`, incorrect Gateway technology and
ports, and omit the Runtime service. CAPO creates isolated units under
`deploy/CAPO/systemd/` and does not overwrite them.

## Duplicate and legacy inventory

| Legacy/current duplicate | Canonical owner | Current evidence | Decision |
|---|---|---|---|
| `control-plane/` | `control/` | 12 textual references; stub HTTP/gRPC/runtime clients | Inventory unique behavior, then selectively port behind Control interfaces |
| `rust-runtime/` | `runtime-daemon/` | 9 textual references; older isolation layout | Compare module-by-module; port only stricter/unique enforcement with Rust tests |
| `database/`, `db/` | `data/` | 16 combined path references; compatibility/data assets | Keep bridges; move callers before any retirement proposal |
| root `models/` | `registry/models/` | 19 references; mirrored metadata plus compatibility client | Registry is writable truth; preserve read compatibility and detect divergence |
| duplicate proto trees | `schemas/` source, `shared/` generated | two explicit `schemas/v1/protos` references | Select one source proto per contract; regeneration required before retirement |
| deployment copies under `execution/` | `deploy/` | four direct references plus broken symlink-like entries | Diff first; CAPO adds only under `deploy/CAPO/` |
| `ui` | `console/`/`packages/ui-core` | compatibility link represented in tracked snapshot | Preserve; CAPO uses `console/` directly |
| `process-analytics` | unresolved historical target | broken compatibility link | Quarantine in reconstruction map; no deletion |

## Historical recovery finding

Commit `5fa2b9c0` removed broad areas including Control APIs, agent catalog, memory,
RAG, policy, CLI, kernel, process analytics, service modules, scripts and generated
contracts. The backup bundle retains those objects. Recovery must be capability-led:

1. prove a missing current requirement;
2. identify the last trustworthy source commit/path;
3. inspect dependencies, security assumptions and schema age;
4. port the minimum behavior into a canonical module;
5. add compatibility and regression tests;
6. validate Native and Quickstart independently.

Restoring `control/os`, `kernel/`, or another deleted root wholesale would recreate
the split architecture and is prohibited by the CAPO recovery contract.

## Security review

- No destructive disk commands are permitted in source or execution paths.
- CAPO scripts may contain bounded `sudo`, package and systemd commands for Linux,
  but automation on Windows must never execute them.
- Environment examples contain placeholders only; secrets remain outside Git.
- Native services run as a dedicated non-root `omertaos` user.
- Runtime remains the only privileged execution boundary.
- Direct Console-to-Control/Runtime access remains prohibited.

## Items intentionally unchanged

No production code, API, auth/permission logic, schema, database, Compose file,
systemd unit, legacy directory, symlink, generated proto or deployment asset was
changed during phase 1.
