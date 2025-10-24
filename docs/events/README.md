# AION-OS Event Contracts

All AION-OS streaming contracts are managed in the Schema Registry using versioned Avro schemas. Schemas are stored in `bigdata/schemas/` and registered against Kafka topics before producers are allowed to publish events.

## Topics

### `aion.router.decisions`
- **Key:** `task_id`
- **Value Schema:** [`RouterDecision`](../../bigdata/schemas/aion.router.decisions.avsc)
- **Description:** Captures the router's selection of execution path for each task, including feature budgets and metadata.

### `aion.tasks.lifecycle`
- **Key:** `task_id`
- **Value Schema:** [`TaskLifecycle`](../../bigdata/schemas/aion.tasks.lifecycle.avsc)
- **Description:** Reflects status transitions for orchestrated tasks across the platform.

### `aion.metrics.runtime`
- **Key:** `component`
- **Value Schema:** [`RuntimeMetric`](../../bigdata/schemas/aion.metrics.runtime.avsc)
- **Description:** Operational metrics from core subsystems, exported for SRE dashboards and anomaly detection.

### `aion.audit.activity`
- **Key:** `actor_id`
- **Value Schema:** [`AuditActivity`](../../bigdata/schemas/aion.audit.activity.avsc)
- **Description:** Immutable audit log for user and system actions touching critical resources.

## Versioning Policy
- Schemas must be backward-compatible; use optional fields with defaults for additive changes.
- Every schema version increment requires publishing release notes in `docs/events/changelog.md`.
- Contract tests validate producer/consumer compatibility as part of CI.
