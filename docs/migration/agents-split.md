# S3.3 migration — Agents split

Date: 2026-07-12

Status: root `agents/` is compatibility-only; no Agent behavior or metadata was
present to migrate.

## Impact analysis

- Tracked input: `agents/__init__.py` only (26 bytes before clarification).
- Database, API, UI, auth and permission impact: none.
- Deployment and Runtime impact: none.
- Risk: low for the root classification; future Agent Registry/lifecycle work is
  high risk and is not authorized by S3.3.
- Gate S2 remains open because Runtime Cargo build cannot reach crates.io.

## File classification

The only tracked root file was a generic package marker. Its blob was identical
to `algorithms/__init__.py` and `registry/__init__.py`. It contained no manifest,
planning logic, SDK, adapter, executable payload, imports, classes or functions.
It now states that the root is a legacy compatibility package and exports
nothing.

No directory was populated speculatively. When real Agent artifacts are
recovered or developed in a later approved feature phase, ownership is mandatory:

| Behavior class | Canonical owner |
|---|---|
| Immutable Agent manifests, versions and lifecycle metadata | `registry/agents/` |
| Planning, resolution, scheduling and lifecycle decisions | `control/agents/` |
| Public authoring/runtime-neutral SDK | `packages/agent-sdk/` |
| External framework/provider adapters | `integrations/agents/` |
| Executable bundles and host-side enforcement | `runtime-daemon/` plus versioned bundle definitions |

Registry metadata must not contain executable logic or plaintext credentials.
Control must not execute processes. SDK code must not depend on Control internals.
Integrations cannot become an alternate Gateway. Runtime cannot select Agents or
interpret business policy.

## Historical Agent Catalog

`tests/test_agent_catalog_api.py` references the removed `os.control` namespace;
no implementation exists in the current tree. Reconstructing that catalog would
be feature recovery, not splitting content from root `agents/`. The test now
skips explicitly at collection with this reason instead of failing import or
creating an illusion that Agent Catalog acceptance passed.

Console Agent routes and Windows Bridge HTTP paths are API consumers, not root
Agent implementations, and were intentionally unchanged.

## Validation

```powershell
python -m pytest tests/architecture/test_agent_split.py tests/test_agent_catalog_api.py -q
python -m pytest tests/architecture tests/control -q
python -m ruff check agents tests/architecture/test_agent_split.py tests/test_agent_catalog_api.py
```

The Structure completion gate remains expected-red while protected roots exist.
S3.3 does not claim Agent Registry, lifecycle or deployment feature acceptance.

## Migration and rollback

No database migration is required. Revert the S3.3 commit to restore the generic
package marker and previous collection error. Do not delete the root package or
add Agent behavior there; permanent retirement remains an S5 action requiring
explicit human approval.
