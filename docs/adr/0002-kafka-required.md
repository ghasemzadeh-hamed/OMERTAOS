# ADR 0002: Kafka as Required Backbone

## Context

Routing, auditing, and metrics need durable streaming.

## Decision

Standardize on Apache Kafka for all event flows. Topics include decisions, lifecycle, metrics, and audit.

## Consequences

- Adds operational overhead but ensures replayable history.
- Enables Spark/Flink integrations for analytics.
