#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

GATEWAY_PORT="${AION_GATEWAY_PORT:-8080}"
GATEWAY_URL="${NEXT_PUBLIC_GATEWAY_URL:-}"
if [[ -z "${GATEWAY_URL}" ]]; then
  GATEWAY_URL="http://localhost:${GATEWAY_PORT}"
elif [[ "${GATEWAY_URL}" =~ ^https?://(gateway|control|console|minio|postgres|redis|qdrant)(:|/|$) ]]; then
  GATEWAY_URL="http://localhost:${GATEWAY_PORT}"
fi
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

payload=$(cat <<'JSON'
{
  "intent": "diagnostics",
  "params": {
    "input": {
      "prompt": "ping"
    }
  },
  "metadata": {
    "source": "smoke-test"
  }
}
JSON
)
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

normalise_status() {
  tr '[:upper:]' '[:lower:]'
}

is_success_status() {
  local value=$1
  case "$value" in
    completed|ok|success)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

is_failure_status() {
  local value=$1
  case "$value" in
    failed|error)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

final_status=""
final_response=""

for i in {1..60}; do
  status_response=$(curl -fsS "$GATEWAY_URL/v1/tasks/$task_id" -H "x-api-key: $API_KEY")
  status=$(echo "$status_response" | jq -r '.status' 2>/dev/null || echo "unknown")
  normalised_status=$(echo "$status" | normalise_status)
  echo "status: $status"

  if is_success_status "$normalised_status"; then
    final_status="$status"
    final_response="$status_response"
    echo "$status_response"
    break
  fi

  if is_failure_status "$normalised_status"; then
    echo "$status_response"
    echo "Task failed with status $status" >&2
    exit 1
  fi

  sleep 5
  if [[ $i -eq 60 ]]; then
    echo "Task did not complete in time" >&2
    exit 1
  fi
done

if [[ -z "$final_status" ]]; then
  echo "Task status did not reach a terminal state" >&2
  exit 1
fi

echo "Streaming events sample"
stream_output=$(curl -fsS -N "$GATEWAY_URL/v1/stream/$task_id" -H "x-api-key: $API_KEY" --max-time 5 || true)
if [[ -z "$stream_output" ]]; then
  echo "No stream output received" >&2
  exit 1
fi

echo "$stream_output" | head -n 5

echo "Smoke test completed"
