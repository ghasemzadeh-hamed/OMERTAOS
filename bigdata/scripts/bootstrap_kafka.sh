#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${KAFKA_BROKERS:-}" ]]; then
  echo "KAFKA_BROKERS must be set" >&2
  exit 1
fi

SCHEMA_REGISTRY=${KAFKA_SCHEMA_REGISTRY:-http://localhost:8081}
RETENTION=${KAFKA_TOPIC_RETENTION_MS:-604800000}
PARTITIONS=${KAFKA_TOPIC_PARTITIONS:-3}

create_topic() {
  local topic="$1"
  kafka-topics \
    --bootstrap-server "$KAFKA_BROKERS" \
    --create \
    --if-not-exists \
    --replication-factor 1 \
    --partitions "$PARTITIONS" \
    --config "retention.ms=$RETENTION" \
    --topic "$topic"
}

register_schema() {
  local subject="$1"
  local schema_file="$2"
  curl -s -X POST "$SCHEMA_REGISTRY/subjects/$subject/versions" \
    -H "Content-Type: application/vnd.schemaregistry.v1+json" \
    -d "{\"schema\":$(jq -Rs . < "$schema_file")}" >/dev/null
}

create_topic aion.router.decisions
create_topic aion.tasks.lifecycle
create_topic aion.metrics.runtime
create_topic aion.audit.activity

register_schema aion.router.decisions-value ../schemas/router_decision.avsc
register_schema aion.tasks.lifecycle-value ../schemas/task_lifecycle.avsc
register_schema aion.metrics.runtime-value ../schemas/metrics_runtime.avsc
register_schema aion.audit.activity-value ../schemas/audit_activity.avsc

echo "Kafka topics and schemas bootstrapped"
