#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  # shellcheck disable=SC1091
  source .env >/dev/null 2>&1 || true
fi

CONTROL_BASE="${CONTROL_BASE_URL:-${NEXT_PUBLIC_CONTROL_BASE:-http://localhost:8000}}"
AGENT_TOKEN="${AGENT_API_TOKEN:-${NEXT_PUBLIC_AGENT_API_TOKEN:-}}"
COLLECTION="${AIONOS_RAG_COLLECTION:-demo-docs}"

say() {
  printf '\n%s\n' "$1"
}

say "== Control health check =="
curl -fsS "$CONTROL_BASE/healthz" || {
  echo "Control plane is not reachable at $CONTROL_BASE" >&2
  exit 1
}

say "== Agent demo =="
agent_payload='{"goal":"List demo tasks","context":{"user":"smoke"}}'
if [ -n "$AGENT_TOKEN" ]; then
  curl -fsS -X POST "$CONTROL_BASE/agent/run" \
    -H "content-type: application/json" \
    -H "x-agent-token: $AGENT_TOKEN" \
    -d "$agent_payload"
else
  curl -fsS -X POST "$CONTROL_BASE/agent/run" \
    -H "content-type: application/json" \
    -d "$agent_payload"
fi

say "== RAG collections before ingest =="
curl -fsS "$CONTROL_BASE/rag/collections" || true

say "== RAG ingest README snippet =="
readme_sample=$(head -n 120 README.md)
curl -fsS -X POST "$CONTROL_BASE/rag/ingest" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "col=$COLLECTION" \
  --data-urlencode "text=$readme_sample" || true

say "== RAG query demo =="
query_payload=$(jq -n --arg col "$COLLECTION" --arg q "What is AION-OS?" '{collection:$col,query:$q,limit:3}' 2>/dev/null || printf '{"collection":"%s","query":"%s","limit":3}' "$COLLECTION" "What is AION-OS?" )
curl -fsS -X POST "$CONTROL_BASE/rag/query" \
  -H "content-type: application/json" \
  -d "$query_payload" || true

say "Smoke test complete."
