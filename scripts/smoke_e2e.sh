#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

GATEWAY_URL="${NEXT_PUBLIC_GATEWAY_URL:-http://localhost:8080}"
CONTROL_URL="${CONTROL_BASE_URL:-${NEXT_PUBLIC_CONTROL_BASE:-http://localhost:8000}}"
CONSOLE_URL="${NEXTAUTH_URL:-http://localhost:3000}"
API_KEY_PAIR="${AION_GATEWAY_API_KEYS:-demo-key:admin|manager}"
API_KEY="${API_KEY_PAIR%%:*}"

wait_for() {
  local name=$1
  local url=$2
  echo "Waiting for $name at $url"
  for i in {1..60}; do
    if curl -fsS "$url" >/dev/null; then
      echo "$name healthy"
      return 0
    fi
    sleep 5
  done
  echo "$name did not become ready" >&2
  return 1
}

wait_for "control" "$CONTROL_URL/healthz"
wait_for "gateway" "$GATEWAY_URL/healthz"
wait_for "console" "$CONSOLE_URL/healthz"

payload='{"intent":"diagnostics","input":{"prompt":"ping"}}'
response=$(curl -fsS -X POST "$GATEWAY_URL/v1/tasks" \
  -H "content-type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d "$payload")

task_id=$(echo "$response" | jq -r '.taskId' 2>/dev/null || echo "")
if [[ -z "$task_id" || "$task_id" == "null" ]]; then
  echo "Failed to create task via gateway" >&2
  echo "$response"
  exit 1
fi

echo "Task created: $task_id"

for i in {1..60}; do
  status_response=$(curl -fsS "$GATEWAY_URL/v1/tasks/$task_id" -H "x-api-key: $API_KEY")
  status=$(echo "$status_response" | jq -r '.status' 2>/dev/null || echo "unknown")
  echo "status: $status"
  if [[ "$status" == "completed" || "$status" == "failed" ]]; then
    echo "$status_response"
    break
  fi
  sleep 5
  if [[ $i -eq 60 ]]; then
    echo "Task did not complete in time" >&2
    exit 1
  fi
done

echo "Streaming events sample"
stream_output=$(curl -fsS -N "$GATEWAY_URL/v1/stream/$task_id" -H "x-api-key: $API_KEY" --max-time 5 || true)
if [[ -z "$stream_output" ]]; then
  echo "No stream output received" >&2
  exit 1
fi

echo "$stream_output" | head -n 5

echo "Smoke test completed"
