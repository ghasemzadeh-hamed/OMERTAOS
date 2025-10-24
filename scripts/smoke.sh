#!/usr/bin/env bash
set -euo pipefail
API_URL=${API_URL:-http://localhost:8080}
API_KEY=${API_KEY:-demo-key}

function submit_task() {
  curl -sS -X POST "$API_URL/v1/tasks" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"hello world"}}'
}

function stream_task() {
  local task_id=$1
  curl -sS "$API_URL/v1/stream/$task_id" -H "X-API-Key: $API_KEY" --no-buffer | head -n 5
}

function reload_policy() {
  curl -sS -X POST "$API_URL/v1/router/policy/reload" -H "X-API-Key: $API_KEY"
}

response=$(submit_task)
echo "Task response: $response"
task_id=$(echo "$response" | jq -r '.taskId // .task_id')
if [[ -n "$task_id" && "$task_id" != "null" ]]; then
  echo "Streaming task $task_id"
  stream_task "$task_id"
fi
reload_policy
