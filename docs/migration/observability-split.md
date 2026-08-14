# S3.6 migration — Observability split

Date: 2026-07-15

Status: Python observability ownership is split across stable telemetry
primitives, exporter integrations and deployment assets. Root `observability/`
and `shared/event_bus/` are compatibility-only until their retirement gates.

## Impact analysis

- `AuditEntry`, `emit_audit` and the synchronous in-process telemetry bus now
  live under `shared/telemetry/`.
- The asynchronous external exporter boundary now lives under
  `integrations/observability/`.
- Prometheus, OpenTelemetry Collector and Grafana assets remain owned by
  `deploy/observability/`.
- Control Network imports the canonical audit primitive, and its image no longer
  copies the root `observability/` compatibility package.
- Database objects, API responses, UI, authentication, permissions, service
  topology, dependencies and secret handling are unchanged.
- Risk is medium because a Control import and shared runtime boundary changed.

## Ownership

| Concern | Canonical owner |
|---|---|
| Audit record and in-process telemetry primitives | `shared/telemetry/` |
| External telemetry exporter boundary/adapters | `integrations/observability/` |
| Service-specific instrumentation | The instrumented service |
| Collector, metrics and dashboard deployment | `deploy/observability/` |
| Historical Python imports | `observability/`, `shared/event_bus/` |

The root placeholder README directories contain no implementation and remain
protected compatibility inputs. Deployment duplicates under `execution/` are
also preserved for S4; S3.6 does not authorize deployment consolidation or
deletion.

## Compatibility and limitations

Legacy modules re-export the canonical objects, preserving import and class
identity. The old synchronous `EventBus` name resolves to `TelemetryBus`; it is
not the asynchronous domain Event Bus introduced in S3.5.

`emit_audit` still returns an in-memory record. It does not persist, sign or
export audit records and must not be presented as durable security auditing.
Adding an OTLP/Kafka/other exporter requires an approved capability slice with
bounded buffering, redaction, retry/backpressure and secret-safe configuration.

Audit records retain actor and tenant scope. No raw request payload, credential,
API key or secret value was added to telemetry or logs.

## Validation

```powershell
python -m pytest tests/architecture/test_observability_split.py tests/control/test_network_proxies_api.py -q
python -m pytest tests/architecture tests/control -q -k "not test_structure_migration_gate"
python -m ruff check shared/telemetry integrations/observability observability shared/event_bus tests/architecture/test_observability_split.py
# The Dockerfile boundary is asserted statically; this phase does not build an image.
```

S3.6 does not claim running collector/Grafana acceptance, durable audit delivery,
Native validation or cleanup of deployment duplicates.

## Migration and rollback

No data migration is required. Existing imports remain valid through wrappers;
new code must use canonical owners.

Rollback consists of reverting the S3.6 changes and restoring the previous
Control import and Dockerfile copy. Do not delete root compatibility paths or
deployment copies. Permanent removal requires zero active callers, S4/S5 gates,
Native and Quickstart acceptance, and explicit human approval.
