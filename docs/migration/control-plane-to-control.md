# S2.1 migration — control-plane to Control

Date: 2026-07-12

Status: canonical behavior migrated; legacy root retained as compatibility input
until the S5 deletion gate.

## Impact analysis

- Canonical owner: `control/`
- Legacy input: `control-plane/`
- Public HTTP impact: none; `/health`, `/healthz`, `/v1/health` and
  `/v1/healthz` retain their existing payload.
- Database impact: none.
- Permission impact: none.
- Security impact: legacy synthetic Runtime success and no-op gRPC startup are
  replaced by fail-closed canonical facades.

## File disposition

| Legacy file | Canonical disposition |
|---|---|
| `runtime_client/runtime_client.py` | Models and bounded facade moved to `control/clients/runtime/client.py` |
| `runtime_client/__init__.py` | Compatibility export points to canonical client |
| `services/http_api.py` | Compatibility export points to `control/app/health.py` |
| `services/grpc_adapter.py` | Compatibility export points to `control/transports/grpc.py` |
| `services/__init__.py` | Compatibility-only package marker |

The Control test suite also referenced the already-removed `os.control`
namespace. Its tested CORS parsing contract now lives in `control/config.py`;
the unrelated historical secret/database configuration was not blindly restored.

The legacy Runtime implementation was not copied verbatim because it returned
`ok: true` without contacting Runtime. The canonical client requires an injected
versioned transport, validates identity/arguments, enforces a timeout and raises
`RuntimeTransportUnavailable` when transport generation/wiring is incomplete.
The old gRPC adapter similarly returned without serving; its canonical facade
raises until a real server factory is supplied.

## Configuration

`AION_RUNTIME_ENDPOINT` is the Control-to-Runtime destination. Quickstart uses
`runtime:50051`; Native uses `127.0.0.1:50051`. This is distinct from
`AION_RUNTIME_BIND_ADDR`, which configures the Runtime server listener.

## Validation

Run:

```powershell
python -m pytest tests/control/test_runtime_client.py tests/control/test_transport_adapters.py -q
python -m pytest tests/control -q
python -m pytest tests/architecture -q
docker compose -f docker-compose.quickstart.yml config --quiet
```

The S1 migration-completion test remains expected-red because the protected
legacy root still exists and S2.2-S5 have not completed. Immediate architecture
invariants must remain green.

## Migration and rollback

No database migration is required. To roll back S2.1, revert its commit as one
unit; the previous legacy stubs remain recoverable in Git and the verified CAPO
backup. Do not delete the compatibility root, configuration, accounts, databases
or persistent state. Permanent path removal remains an S5 action requiring human
approval and full Native/Quickstart acceptance.
