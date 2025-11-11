# Event Streams

## Kafka Topics

| Topic                   | Key         | Schema                                       | Description                                    |
| ----------------------- | ----------- | -------------------------------------------- | ---------------------------------------------- |
| `aion.router.decisions` | `task_id`   | `schemas/events/router_decision.schema.json` | Records router choices and privacy tier        |
| `aion.tasks.lifecycle`  | `task_id`   | `schemas/events/tasks_lifecycle.schema.json` | Tracks task state transitions                  |
| `aion.metrics.runtime`  | `component` | `schemas/events/metrics_runtime.schema.json` | Emits metrics for Prometheus-style aggregation |
| `aion.audit.activity`   | `actor_id`  | `schemas/events/audit_activity.schema.json`  | Captures administrative changes                |

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

Use `bigdata/scripts/bootstrap_kafka.sh` to create topics with retention policies and register schemas with the Confluent-compatible Schema Registry.

## Webhooks

Outbound webhooks configured in `policies/webhooks.yaml` mirror the Kafka catalog. Each webhook entry includes:

- `url` – HTTPS endpoint that receives the event payload.
- `secret` – shared HMAC-SHA256 secret used to populate the `X-Aion-Signature` header.
- `topics` – list of topic patterns (for example, `kernel.proposal.*`) that trigger deliveries.
- `retry` – backoff configuration (`initial_interval`, `max_interval`, `max_attempts`).

Deliveries include an `Idempotency-Key` header and are retried automatically until success or the retry policy expires.

Inbound commands arrive on `/webhooks/inbound` inside the gateway. Only allow-listed actions such as `approve_kernel_proposal`,
`reject_kernel_proposal`, `install_module`, `ingest_dataset`, and `update_memory_profile` are executed. Requests must pass HMAC
verification and RBAC checks (API key or JWT) before being dispatched to the control plane. Every accepted command emits an aud
it event.
