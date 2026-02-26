# API_REFERENCE

> Runtime alignment: Python control-plane delegates OS-level execution/isolation/sandbox to Rust `runtime-daemon` over gRPC (`shared/proto/runtime.proto`).


## Authentication
Authentication requirements vary by route group (admin/devops/user/service tokens). Review middleware and route dependencies in control API modules.

## Endpoint Map (selected)
| Method | Path | Description |
|---|---|---|
| GET | `/healthz` | Control health check |
| GET | `/api/healthz` | API scoped health |
| GET | `/metrics` | Prometheus metrics (if enabled) |
| GET | `/api/models` | List local + registry models |
| POST | `/api/models/install` | Install model from URL/registry |
| POST | `/api/models/remove` | Remove local model |
| GET | `/api/services` | Service status overview |
| GET | `/api/logs` | Service log streams |
| GET | `/api/datasets` | Dataset listing |
| POST | `/api/backup/create` | Trigger backup |
| POST | `/api/update/run` | Trigger update |

## Example cURL Calls
```bash
curl -s http://localhost:8000/healthz
```

```bash
curl -s -X POST http://localhost:8000/api/models/install   -H 'Content-Type: application/json'   -d '{"name":"example-model.bin","source":"url","url":"https://example.invalid/model.bin"}'
```

## Request/Response and Errors
- Request schemas are route-specific and defined in control modules.
- Common errors: `400` invalid payload, `401/403` auth failure, `404` resource missing, `502` downstream failure.

## Full Endpoint Source Snapshot
For the auto-discovered endpoint list, see [migration/api_endpoints_snapshot.md](../migration/api_endpoints_snapshot.md).
