# Architecture Blueprint

## 0. Strategic Summary
- **Tenancy**: Begin single-tenant but keep all schemas, claims, and storage namespaces `tenant_id`-ready.
- **AuthN/Z**: API Key and JWT first, optional OIDC later; short-lived tokens with rotation; RBAC/ABAC via policy engine.
- **Execution**: Default to WASM (WASI) modules; fall back to hardened subprocesses for GPU/native needs; package via OCI/ORAS with cosign signatures and SBOMs.
- **Accelerators**: First-class support for NVIDIA CUDA/cuDNN, AMD ROCm, and Intel oneAPI/Level-Zero.
- **Data & Streams**: Postgres + Mongo (metadata/logs), Kafka (required events), Qdrant (vector), MinIO (object).
- **Interfaces**: REST, WS/SSE, and public+internal gRPC; schema-first with versioning.
- **Data Residency**: Client-selectable policies (`local-only`, `allow-api`, `hybrid`).
- **Providers**: All model vendors allowed; tiered defaults with per-intent overrides.

## 1. Logical Architecture
```
[ Clients / SDKs / CLI ]
        |  REST / WS / gRPC
        v
+------------------------------+
| Node.js Gateway (TS)         |  Auth, RateLimit, TLS/mTLS, Idempotency, SSE/WS
+---------------+--------------+
                | REST+traceparent / gRPC
                v
+------------------------------+
| FastAPI Control Plane        |  AI Decision Router, Orchestrator, Policy, Memory
+-------+-----------+----------+
        |           |
  gRPC  |           | REST/gRPC
        v           v
 [WASM/Subproc Modules (Rust)]   [LLMs: OpenAI/Azure/HF/Ollama/vLLM]
              |
              | Events (Kafka, required)
              v
        [ Kafka Topics ] --> [ Spark/Flink ] --> [ ClickHouse + MinIO ]
                      \--> [ Superset/Grafana/Metabase ]
```

### Key Points
- Gateway handles edge concerns only: auth, rate limiting, streaming, backpressure.
- Control plane performs routing, orchestration, memory, and policy enforcement.
- Modules run as WASM by default; subprocesses only when platform features demand.
- Kafka is mandatory for events, feeding analytics stacks like Spark/Flink and ClickHouse.

## 2. Module Execution Model
### 2.1 AIP Manifest Template
```yaml
apiVersion: aionos/v1
kind: AgentPackage
metadata:
  name: summarize_text
  version: "1.3.0"
  authors: ["AION Core"]
  license: Apache-2.0
  signatures:
    cosign: "sigstore://ghcr.io/aion/summarize_text@sha256:..."
  sbom: "oci://ghcr.io/aion/sbom/summarize_text:1.3.0"
runtime:
  type: wasm
  wasi: true
  resources:
    cpu: "0.5"
    memory: "256Mi"
    gpu:
      required: false
      vendor: none
permissions:
  filesystem: read-only
  network: deny
  secrets: ["OPENAI_API_KEY?"]
entrypoints:
  grpc:
    port: 0
  schema:
    input: "schemas/summarize_input.json"
    output: "schemas/summarize_output.json"
intents:
  - "summarize"
policies:
  timeout_ms: 1500
  retries: 0
```

### 2.2 WASM Runtime
- Use wasmtime/wasmedge with WASI.
- Restrict host calls (clock, random, logging) and gate network via manifest.
- Request context delivered via JSON stdin or in-process gRPC ABI.

### 2.3 Subprocess Fallback
- Required for GPU bindings, system calls, or libraries unsupported in WASM.
- Sandbox with unprivileged users, seccomp/AppArmor, cgroups, read-only FS, and egress deny unless allowlisted.
- Contract uses JSON over stdio or loopback gRPC.

### 2.4 Distribution
- Package modules via ORAS/OCI without Docker runtime dependencies.
- Enforce cosign signatures and SBOM validation before installation; quarantine unknown packages.

## 3. API Contracts
### 3.1 REST
- `POST /v1/tasks` accepts task metadata, SLA, and preferences with idempotency support.
- `GET /v1/tasks/{task_id}` retrieves status and output.
- `GET /v1/stream/{task_id}` offers SSE/WS streaming for partial tokens.

**Canonical Result JSON**
```json
{
  "schema_version": "1.0",
  "task_id": "uuid",
  "intent": "summarize",
  "status": "OK|ERROR|TIMEOUT|CANCELED",
  "engine": {
    "route": "local|api|hybrid",
    "chosen_by": "ai-router|policy-override",
    "reason": "..."
  },
  "result": { "summary": "..." },
  "usage": { "latency_ms": 523, "tokens": 1423, "cost_usd": 0.0018 },
  "error": null
}
```

### 3.2 gRPC
```proto
syntax = "proto3";
package aion.v1;

message TaskRequest {
  string schema_version = 1;
  string task_id = 2;
  string intent = 3;
  map<string, string> params = 4;
  string preferred_engine = 5;
  string priority = 6;
  SLA sla = 7;
  map<string, string> metadata = 8;
}
message SLA {
  double budget_usd = 1;
  int32 p95_ms = 2;
  string privacy = 3;
}
message Usage { int64 latency_ms = 1; int64 tokens = 2; double cost_usd = 3; }
message Engine { string route = 1; string chosen_by = 2; string reason = 3; }
message Error { string code = 1; string message = 2; }

message TaskResult {
  string schema_version = 1;
  string task_id = 2;
  string intent = 3;
  string status = 4;
  Engine engine = 5;
  string result_json = 6;
  Usage usage = 7;
  Error error = 8;
}

service AionTasks {
  rpc Submit(TaskRequest) returns (TaskResult);
  rpc Stream(TaskRequest) returns (stream TaskResult);
  rpc StatusById(TaskId) returns (TaskResult);
}
message TaskId { string task_id = 1; }
```
- Authenticate via mTLS and JWT metadata.
- Version namespace `aion.v1`; only add fields in new versions.

### 3.3 Streaming
- WebSocket endpoint `/v1/ws` with subscribe pattern.
- SSE standard events `token`, `partial`, `done`, `error`.

## 4. AI Decision Router
- Tier-based providers (local, cloud-standard, cloud-premium) selected by intent, privacy, budget, and SLA.
- Router prompt ensures deterministic JSON decisions.
- Policy engine can override or deny providers.
- Safe fallbacks prefer local before escalating to cloud tiers.

## 5. Data Stores & Streams
- Postgres tables: `agents`, `tasks`, `policies`, `modules`, `models`, `usage_billing`, `audit_activity`; add `tenant_id` for multi-tenant.
- Mongo for structured logs with TTL indices.
- Kafka topics with schema registry and SASL/mTLS security.
- Qdrant namespaces per tenant; MinIO buckets for raw/processed/features/models with lifecycle policies.

## 6. Observability
- OTEL traces across gateway, control, and modules.
- Prometheus metrics: RPS, latency, error rates, queue depth, GPU utilization.
- Grafana dashboards for routing, task health, and resource usage.
- Log retention: Dev 7-14 days, Prod 30-90 days using Mongo and ClickHouse TTL.

## 7. Security & Governance
- API keys for services; JWT for users; optional OIDC.
- RBAC/ABAC with policy-driven restrictions.
- Secrets via Vault/SOPS with rotation.
- PII masking in logs, policy-driven privacy controls.
- Supply chain hardening with cosign, SBOM, and security scans.
- Network mTLS and default egress deny; allowlist providers.
- Rate limiting per API key and IP with token buckets.

## 8. Concurrency & Backpressure
- Gateway uses PM2 cluster, manages WS backpressure and graceful deploys.
- Control plane scales with Uvicorn/Gunicorn workers and returns 429/503 during saturation.
- Modules enforce per-replica concurrency and circuit breakers.

## 9. Multi-Tenant Migration
- Add `tenant_id` to schemas, claims, and storage namespaces.
- Backfill `tenant_id` with `default` for existing data.
- Namespace Qdrant, Redis, MinIO, Kafka by tenant.
- Gateway infers tenant from auth headers.
- Apply per-tenant quotas.

## 10. Capacity & SLOs
- Baseline production target: 200 RPS (60% local, 30% API, 10% hybrid).
- Latency goals: local ≤500 ms, API ≤2000 ms, hybrid ≤2300 ms.
- Availability ≥99.5%, success ≥99% per 24h.

## 11. Operational Runbook Summary
1. Boot stack (compose or k8s) and verify `/healthz` endpoints.
2. Load secrets via Vault/SOPS; verify cosign.
3. Apply policies (`intents.yml`, `policies.yml`, etc.).
4. Enable observability (Prom/Grafana, OTEL traces).
5. Provision Kafka topics with ACLs; run smoke producer/consumer.
6. Install sample modules via `aionctl` and run smoke tests.
7. Maintain rollback via versioned configs and policy reload endpoint.
8. Incident response: apply circuit breakers, reroute tiers, toggle `local-only`.

## 12. Testing & Acceptance
- Validate JSON schemas and protobuf contracts.
- Functional coverage for local/api/hybrid paths, streaming, cancellation.
- Load testing at 200 RPS with backpressure scenarios.
- Chaos tests for provider slowness, module crashes, stream interruption.
- Security checks for authz, injection, package signing, and sandboxing.
- Data pipeline verification from Kafka → ClickHouse/MinIO → dashboards.

## 13. Policy & Registry Examples
Refer to [docs/reference-manifests.md](./reference-manifests.md) for YAML samples of intents, policies, models, and modules.

## 14. Key Sequences
- Task submission path from client through router to modules and analytics.
- Policy reload workflow from data team to control plane.

## 15. Rate Limiting & Idempotency
- Redis-backed token buckets: per API key 60 rpm (burst 120), per IP 120 rpm.
- Cache idempotent results for 5–15 minutes to avoid duplicate execution/charges.

## 16. Deployment Paths
- **Docker Compose**: dev stack including optional ML services and analytics.
- **Kubernetes**: separate deployments, service mesh, ConfigMaps/Secrets, GPU node pools.

## 17. Delivery Checklist
- Provide schemas, manifests, dashboards, smoke tests, and security profiles for handoff.
