# S3.5 migration — Event Bus split

Date: 2026-07-15

Status: Event Bus ownership is split across canonical contracts, Control ports
and integration adapters; root `eventbus/` is compatibility-only until S5.

## Impact analysis

- Contract schemas remain authored under `schemas/v1/events/`.
- The transport-neutral Python port and envelope now live in
  `control/ports/event_bus.py`.
- In-process and Kafka adapters now live under `integrations/eventbus/`.
- Existing `eventbus.interface`, `eventbus.local_bus` and `eventbus.kafka_bus`
  imports remain valid through identity-preserving compatibility exports.
- Database objects, public APIs, UI, authentication, permissions, deployment
  topology and dependencies are unchanged.
- Risk is medium because a shared cross-service boundary moved, although active
  callers were limited to the legacy Event Bus package itself.

## Ownership

| Concern | Canonical owner |
|---|---|
| Authored event JSON Schemas | `schemas/v1/events/` |
| Control publishing/consuming abstraction and `DomainEvent` envelope | `control/ports/event_bus.py` |
| In-process development/test adapter | `integrations/eventbus/local.py` |
| Optional Kafka transport boundary | `integrations/eventbus/kafka.py` |
| Historical imports only | `eventbus/` |

The split does not add durable delivery semantics. `LocalEventBus` retains its
existing fire-and-forget behavior and is suitable only for development and
tests. `KafkaEventBus` still fails closed with `NotImplementedError`; wiring a
producer or consumer requires an explicitly approved feature with serialization,
idempotency, retry, ordering and consumer-group contracts.

No adapter may contain Control decisions, and Control must depend on its port
rather than an integration implementation. Durable domain facts still require
the documented transactional outbox/inbox design before production use.

## Compatibility and security

Compatibility modules only re-export canonical symbols and contain no classes
or functions. This preserves object identity for type checks and existing
imports without allowing new behavior in the legacy root.

`DomainEvent` continues to require `tenant_id`; tests verify that dispatch does
not discard tenant scope. Event payloads must not contain credentials or raw
confidential content. Kafka configuration stores only endpoints and topic
prefixes—no secret value was introduced.

## Validation

```powershell
python -m pytest tests/architecture/test_eventbus_split.py -q
python -m pytest tests/architecture -q -k "not test_structure_migration_gate"
python -m ruff check control/ports integrations/eventbus eventbus tests/architecture/test_eventbus_split.py
```

Coverage is reported only if the repository coverage toolchain produces it.
S3.5 does not claim Kafka integration, durable-delivery or running-stack
acceptance.

## Migration and rollback

No database or data migration is required. Consumers may keep legacy imports
during the compatibility window, but all new code must import the Control port
or integration adapter from its canonical owner.

Rollback consists of reverting the S3.5 file changes. Do not delete the root
`eventbus/` package: permanent retirement remains an S5 action requiring zero
callers, compatibility evidence, Native/Quickstart acceptance and explicit
human approval.
