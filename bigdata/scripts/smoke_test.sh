#!/usr/bin/env bash
set -euo pipefail

KAFKA_BROKERS="${KAFKA_BROKERS:-localhost:9092}"
CLICKHOUSE_URL="${CLICKHOUSE_URL:-http://localhost:8123}"
TOPIC="aion.router.decisions"

cat <<MSG | kafka-console-producer --broker-list "$KAFKA_BROKERS" --topic "$TOPIC"
{"task_id":"demo","intent":"code_generation","decision":"local","reason":"smoke-test","policy_overrides":{"is_manual":false,"privacy_override":false,"cost_override":false,"latency_override":false},"features":{"size":1024,"latency_budget":1200,"cost_budget":0.05,"privacy_level":"public"},"engine_meta":{"model":"router-v1","local_module":null,"version":"1.0.0"},"ts_event":$(date +%s%3N)}
MSG

sleep 10

curl -s "$CLICKHOUSE_URL" --data 'SELECT count() FROM aion.decisions WHERE task_id = "demo"' | grep -qv '^0$'
