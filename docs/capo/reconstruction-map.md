# CAPO reconstruction map

This is the provenance and compatibility ledger for selective recovery. It is not
a deletion list. Every future recovery entry must name an exact source commit/path,
destination, callers, tests and rollback before code is copied.

## Recovery rules

1. Verify the external backup checksums and bundle before inspection.
2. Restore historical content only into a temporary directory.
3. Compare current and historical behavior; never overwrite the active repository
   with an extracted archive.
4. Port the smallest unique behavior into the canonical owner.
5. Preserve old imports/routes with a forwarding bridge where consumers remain.
6. Record Native and Quickstart validation separately.
7. Keep retirement/deletion status `pending` until both paths pass on their real
   environments and a human approves the exact removal diff.

## Path-level map

| Legacy source | Canonical destination | Provenance baseline | Current callers/references | Compatibility | Required validation | Retirement |
|---|---|---|---|---|---|---|
| `control-plane/services/` | `control/app/` or explicit Control ports | bundle + current HEAD | Compose/docs/tests audit required per file | HTTP/gRPC adapter, no second app | Control unit/API contracts; Quickstart health; CAPO import/start | pending |
| `control-plane/runtime_client/` | `control/runtime/` | bundle + current HEAD | Gateway/Control gRPC settings | versioned Runtime client facade | deadline/error/negative capability tests | pending |
| historical `control/os/**` | feature-specific `control/*` modules | last pre-`5fa2b9c0` source path | old tests and wrappers remain in history/current tree | canonical facade only; do not recreate `control/os` | targeted feature, auth, tenant and API regression | pending |
| `rust-runtime/**` | `runtime-daemon/src/**` | bundle + current HEAD | CI/docs and legacy build references | no parallel daemon | Cargo build/test, denied capability, sandbox tests, Runtime readiness | pending |
| `database/**` | `data/rag`, `data/vector`, `data/adapters` | bundle + current HEAD | legacy imports and identical files | lazy/re-export bridge | import contracts and adapter integration | pending |
| `db/**` | `data/` or `deploy/` by responsibility | bundle + current HEAD | migrations/big-data references | documented read bridge | schema ownership and data tests | pending |
| `models/**` | `registry/models/**` | bundle + current HEAD | model loader and docs | read-only mirror with equality test | registry validation and `/models` API | pending |
| duplicate task/runtime protos | `schemas/` source; `shared/` generated | bundle + current HEAD | Gateway, Control and Runtime codegen | generated compatibility packages | proto compilation and cross-service contract tests | pending |
| `execution/{compose,k8s,scripts,systemd}` | `deploy/` | bundle + current HEAD | legacy docs/scripts | pointer/docs during transition | manifest diff, Compose config, deployment smoke | pending |
| `execution/windows-agentic-bridge` | `integrations/windows-agentic-bridge` | bundle + current HEAD | integration docs/packages | one external integration facade | server/UI tests and tool authorization review | pending |
| broken `process-analytics` link | target chosen after history audit | bundle historical objects | no valid target in current checkout | none until target is proven | import/API/data ownership tests | blocked |

## File-level recovery entry template

Add one row before each recovered file or coherent file set:

| Capability | Source commit:path | SHA-256 | Canonical destination | Why unique | Callers | Security review | Targeted tests | Native result | Quickstart result | Rollback |
|---|---|---|---|---|---|---|---|---|---|---|
| _pending_ | | | | | | | | | | |

## Acceptance matrix

| Gate | Native CAPO | Docker Quickstart |
|---|---|---|
| Static configuration | pending phase 6 | current config retained; revalidate phase 6 |
| Build | pending Linux toolchain | pending phase 6 rebuild |
| Service readiness | pending real systemd host | pending full stack smoke |
| End-to-end flow | pending | pending |
| Safe retirement approval | blocked until all above pass | blocked until all above pass |
