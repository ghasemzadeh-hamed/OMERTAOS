# Event Streams

## Kafka Topics

| Topic | Key | Schema | Description |
|-------|-----|--------|-------------|
| `aion.router.decisions` | `task_id` | `schemas/events/router_decision.schema.json` | Records router choices and privacy tier |
| `aion.tasks.lifecycle` | `task_id` | `schemas/events/tasks_lifecycle.schema.json` | Tracks task state transitions |
| `aion.metrics.runtime` | `component` | `schemas/events/metrics_runtime.schema.json` | Emits metrics for Prometheus-style aggregation |
| `aion.audit.activity` | `actor_id` | `schemas/events/audit_activity.schema.json` | Captures administrative changes |

## Retention and ACLs

- Default retention: 7 days dev, 30 days prod.
- Enable Kafka ACLs restricting produce/consume to service accounts.
- Use SASL/SCRAM or mTLS for broker authentication.

## Schema Registry

Avro schemas mirror JSON schema definitions and live under `bigdata/schemas`. Register them with Confluent Schema Registry using `schema-registry-client`:

```bash
sr-cli --config schema-registry.properties register --subject aion.router.decisions-value --schema bigdata/schemas/router_decision.avsc
```

## Consumers

- Spark streaming jobs consume decisions and lifecycle events.
- Airflow DAGs ingest ClickHouse exports for offline training.
- Control plane producers validate payloads before publishing.
