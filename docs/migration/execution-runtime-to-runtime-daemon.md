# S2.4 migration — Runtime code from execution

Date: 2026-07-12

Status: the only Runtime source under `execution/` is compatibility-only; all
non-Runtime assets remain protected for their later owner-specific phases.

## Impact analysis

- Canonical execution owner: `runtime-daemon/`
- Canonical caller contract: `control/clients/runtime/`
- Legacy input: `execution/runtime_contract.py`
- Database, API, UI, permission and deployment behavior: unchanged.
- Risk: medium; this changes a prototype contract with no active caller and
  adds no host execution.

## Inventory decision

S2.4 classified all 121 tracked paths under `execution/`. Only
`runtime_contract.py` is Runtime source code. It duplicated tenant, agent and
argv fields already owned by the canonical Control Runtime client.

The file now re-exports canonical `RuntimeEnvelope` as the backward-compatible
`RuntimeCommand` name and the canonical `RuntimeExecutor` Protocol. Legacy list
arguments are normalized to an immutable tuple by the canonical model.

The remaining 120 paths are explicitly outside S2.4:

- systemd, install/backup/restore scripts, Compose, Kubernetes and CI assets are
  deployment inputs for S4;
- bundles and module manifests require supporting-layer ownership review;
- observability assets belong to the observability split;
- Windows Agentic Bridge belongs to `integrations/` and S3;
- capability Compose templates describe optional services, not Runtime
  capability enforcement.

Two orphaned Rust files under `tests/execution/` reference a non-existent
`execution` crate. The sandbox test assumes direct command/WASM success, which
conflicts with the current fail-closed canonical Runtime. They are not wired into
Cargo and remain historical inputs until S5; they are not treated as passing
security evidence.

## Validation

```powershell
python -m pytest tests/control/test_runtime_client.py -q
python -m pytest tests/control -q
python -m pytest tests/architecture/test_runtime_migration.py -q
python -m pytest tests/architecture -q
cargo metadata --manifest-path runtime-daemon/Cargo.toml --no-deps --format-version 1
docker compose -f docker-compose.quickstart.yml config --quiet
```

Cargo compile/test remains blocked on this workstation by unavailable
`index.crates.io:443` and an empty local crate cache, as recorded in S2.3.
Native Linux sandbox acceptance remains mandatory. The Structure completion
gate remains expected-red while protected legacy roots exist.

## Migration and rollback

No database migration is required. Revert the S2.4 commit as one unit to restore
the standalone prototype contract. Do not delete `execution/` assets or either
Runtime tree. Their later migration and permanent removal require separate phase
approval, full diffs and Native/Quickstart acceptance.
