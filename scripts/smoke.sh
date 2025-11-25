#!/usr/bin/env bash
set -euo pipefail
MODE=${MODE:-native}
CONTROL_HEALTH_URL=${CONTROL_HEALTH_URL:-http://localhost:8000/health}
GATEWAY_HEALTH_URL=${GATEWAY_HEALTH_URL:-http://localhost:3000/health}
CONSOLE_HEALTH_URL=${CONSOLE_HEALTH_URL:-http://localhost:3001/health}
SMOKE_RETRIES=${SMOKE_RETRIES:-30}
SMOKE_DELAY=${SMOKE_DELAY:-3}
API_URL=${API_URL:-http://localhost:8080}
API_KEY=${API_KEY:-demo-key}

check_http() {
  local url=$1
  local label=$2
  local unit=${3:-}
  local attempts=$SMOKE_RETRIES
  local delay=$SMOKE_DELAY

  print_control_diagnostics() {
    if [[ "$label" != "control" ]]; then
      return
    fi
    if command -v systemctl >/dev/null 2>&1; then
      local ctl="systemctl"
      local journal="journalctl"
      if command -v sudo >/dev/null 2>&1; then
        ctl="sudo systemctl"
        journal="sudo journalctl"
      fi
      echo "systemctl is-active omerta-control:"
      $ctl is-active omerta-control || true
      echo "Last 200 journalctl lines for omerta-control:"
      $journal -u omerta-control -n 200 --no-pager || true
    fi
  }

  print_service_diagnostics() {
    if [[ -z "$unit" ]] || ! command -v systemctl >/dev/null 2>&1; then
      return
    fi
    local ctl="systemctl"
    local journal="journalctl"
    if command -v sudo >/dev/null 2>&1; then
      ctl="sudo systemctl"
      journal="sudo journalctl"
    fi
    echo "systemctl status $unit:"
    $ctl status "$unit" --no-pager || true
    echo "Last 50 journalctl lines for $unit:"
    $journal -u "$unit" -n 50 --no-pager || true
  }

  for ((i=1; i<=attempts; i++)); do
    if curl -fsS "$url" >/tmp/smoke_response.$$ 2>/tmp/smoke_error.$$; then
      cat /tmp/smoke_response.$$
      rm -f /tmp/smoke_response.$$ /tmp/smoke_error.$$
      return 0
    fi
    echo "[$label] attempt $i/$attempts failed" >&2
    sleep "$delay"
  done

  echo "Failed to reach $label at $url" >&2
  if [[ -s /tmp/smoke_error.$$ ]]; then
    cat /tmp/smoke_error.$$ >&2
  fi
  echo "[diagnostic] curl -v $url" >&2
  curl -v "$url" || true
  print_control_diagnostics
  print_service_diagnostics
  rm -f /tmp/smoke_response.$$ /tmp/smoke_error.$$
  return 1
}

wait_for_service() {
  local unit=$1
  local attempts=$SMOKE_RETRIES
  if ! command -v systemctl >/dev/null 2>&1; then
    return 0
  fi
  local ctl="systemctl"
  if command -v sudo >/dev/null 2>&1; then
    ctl="sudo systemctl"
  fi

  for ((i=1; i<=attempts; i++)); do
    if $ctl is-active --quiet "$unit"; then
      return 0
    fi
    sleep "$SMOKE_DELAY"
  done
  return 1
}

if [[ "$MODE" == "native" ]]; then
  HAVE_JQ=false
  if command -v jq >/dev/null 2>&1; then
    HAVE_JQ=true
  fi

  wait_for_service omerta-control || true
  wait_for_service omerta-gateway || true

  echo "Checking control plane health at $CONTROL_HEALTH_URL"
  response=$(check_http "$CONTROL_HEALTH_URL" "control" "omerta-control")
  if [[ "$HAVE_JQ" == "true" ]]; then
    jq '.status' >/dev/null <<<"$response"
  fi

  echo "Checking gateway health at $GATEWAY_HEALTH_URL"
  response=$(check_http "$GATEWAY_HEALTH_URL" "gateway" "omerta-gateway")
  if [[ "$HAVE_JQ" == "true" ]]; then
    jq '.status' >/dev/null <<<"$response"
  fi

  if [[ "${SKIP_CONSOLE_HEALTH:-false}" != "true" ]]; then
    echo "Checking console availability at $CONSOLE_HEALTH_URL"
    check_http "$CONSOLE_HEALTH_URL" "console" "omerta-console" >/dev/null
  fi

  echo "Native smoke checks passed"

  if [[ "${RUN_GATEWAY_FLOW:-false}" != "true" ]]; then
    exit 0
  fi
fi

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
