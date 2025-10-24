# OMERTAOS Technical Blueprint

## 0. Strategic Summary

- **Tenancy**: Start as single-tenant while designing the schema, claims, and tokens for a seamless upgrade to multi-tenant (add `tenant_id` to key tables and token claims).
- **AuthN/Z**: API Key and JWT first, with optional OIDC/SSO. Combine RBAC and ABAC via a policy engine. Short-lived tokens with rotation.
- **Execution**: Prefer WASM for isolation and portability; fall back to secured subprocesses when native acceleration is required. Package modules as OCI/ORAS artifacts with mandatory signatures (Cosign/Sigstore) and SBOMs.
- **GPU/Acceleration**: Provide first-class support for NVIDIA (CUDA/cuDNN), AMD (ROCm), and Intel (oneAPI/Level-Zero). Capture GPU needs in the AIP manifest.
- **Data & Streams**: Postgres plus Mongo for structured metadata/logs, Kafka for events (required), Qdrant for vectors, MinIO for object storage.
- **Interfaces**: REST, WS/SSE, and public gRPC (in addition to internal gRPC). Version all APIs.
- **Residency/Privacy**: Client-selectable data-residency modes (`local-only`, `allow-api`, `hybrid`).
- **Providers**: All model providers allowed. Default to tier-based routing (local → cost-efficient, cloud → higher IQ) with per-intent overrides.

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

Key points:

- Gateway handles ingress concerns (auth, rate limiting, idempotency, streaming, backpressure).
- Control plane runs routing, orchestration, memory, and cost metering.
- Modules prefer WASM (WASI) with subprocess fallback for GPU/native bindings.
- Big data flow: Kafka topics feed Spark/Flink, landing in ClickHouse and MinIO, surfaced via Superset/Grafana.

## 2. Module Execution Model

### 2.1 AIP Manifest Example

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
  type: wasm            # wasm | subprocess
  wasi: true
  resources:
    cpu: "0.5"
    memory: "256Mi"
    gpu:
      required: false
      vendor: none      # nvidia | amd | intel | none
permissions:
  filesystem: read-only
  network: deny
  secrets: ["OPENAI_API_KEY?"]
entrypoints:
  grpc:
    port: 0             # wasm: in-process; subprocess: fixed port or stdio
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
- Restrict hostcalls (clock, random, logging). Allow networking only if manifest permits it.
- Deliver request context as JSON over stdin or via an in-process gRPC ABI.
- Benefits: portability, strong isolation, minimal runtime dependencies.

### 2.3 Secured Subprocess Fallback

- Use when GPU, system calls, or native libraries are required.
- Sandbox via unprivileged users, seccomp/AppArmor, cgroups, read-only filesystems, and default-deny networking.
- Exchange data through JSON over stdio or gRPC loopback.

### 2.4 Distribution Without Docker Dependency

- Package modules as ORAS/OCI artifacts.
- Sign with Cosign and attach SBOMs; enforce signature and SBOM validation at install time.
- Quarantine unverified packages.

## 3. External Interfaces

### 3.1 REST Endpoints

- `POST /v1/tasks` accepts the canonical task payload with headers for auth (`Authorization`), idempotency, and tracing (`Traceparent`).
- `GET /v1/tasks/{task_id}` and `GET /v1/stream/{task_id}` surface status, results, and streaming updates via SSE/WS.
- Standard task result envelope:

```json
{
  "schema_version": "1.0",
  "task_id": "uuid",
  "intent": "summarize",
  "status": "OK|ERROR|TIMEOUT|CANCELED",
  "engine": {"route": "local|api|hybrid", "chosen_by": "ai-router|policy-override", "reason": "..."},
  "result": {"summary": "..."},
  "usage": {"latency_ms": 523, "tokens": 1423, "cost_usd": 0.0018},
  "error": null
}
```

### 3.2 Public gRPC

- Package: `aion.v1`.
- Services: `Submit`, `Stream`, and `StatusById` using `TaskRequest`/`TaskResult` messages.
- Auth via mTLS plus JWT in metadata.
- Backward compatibility through additive versioning (no breaking removals).

### 3.3 WS/SSE

- WebSocket path `/v1/ws` with `subscribe` operations.
- SSE emits `token`, `partial`, `done`, `error` events.

## 4. AI Decision Router

- Supports tiered provider routing (Tier 0 local, Tier 1 cloud-standard, Tier 2 premium).
- Decision flow: respect privacy (`local-only`), budgets, latency requirements, input features, and policy overrides.
- Prompt-driven router returns `{decision, reason, tier}`. Invalid decisions fall back to a safe route (local → api → hybrid).

## 5. Data and Storage Stack

- **Postgres**: core tables (`agents`, `tasks`, `policies`, `modules`, `models`, `usage_billing`, `audit_activity`). Prepare for multi-tenancy by adding `tenant_id` and composite indexes.
- **MongoDB**: structured logs, session replays, raw event mirrors with TTL indexes.
- **Kafka**: mandatory event backbone with schema registry. Topics include `aion.router.decisions`, `aion.tasks.lifecycle`, `aion.metrics.runtime`, `aion.audit.activity`. Secure with SASL/SCRAM or mTLS and ACLs.
- **Qdrant**: vector store with per-tenant namespaces.
- **MinIO/S3**: object storage buckets (`raw/`, `processed/`, `features/`, `models/`) with lifecycle policies.

## 6. Observability

- OpenTelemetry traces end-to-end (Gateway → Control → Modules/LLMs).
- Prometheus metrics (RPS, latency percentiles, error rates, queue depths, GPU utilization, WS backpressure).
- Grafana dashboards for routing, task health, and resource usage.
- Log retention: 7–14 days in dev, 30–90 days in prod using Mongo and ClickHouse TTLs.

## 7. Security and Governance

- Authentication: API keys for machine clients, short-lived JWTs for users/services, optional OIDC.
- Authorization: RBAC + ABAC with intent/route/provider/tenant constraints.
- Secrets via Vault/SOPS; rotate regularly and never bake secrets into images.
- Privacy: mask PII in logs; enforce `local-only` for sensitive intents.
- Supply chain: mandatory Cosign signatures, SBOMs, and vulnerability scans (Grype/Trivy).
- Networking: internal mTLS, default-deny egress with provider allowlists.
- Rate limiting: token buckets per API key/user/IP with per-second and per-minute quotas.

## 8. Concurrency and Backpressure

- Gateway: PM2 clustering, WS/SSE backpressure handling, keepalive pings, graceful draining.
- Control plane: Uvicorn/Gunicorn workers with bounded internal queues; respond with 429/503 and `Retry-After` when saturated.
- Modules: cap concurrency per replica, enforce cgroups limits, and apply circuit breakers to slow modules.

## 9. Path to Multi-Tenancy

- Add `tenant_id` to Postgres tables, JWT claims, and API key scopes.
- Namespace external stores (Qdrant, Redis, MinIO, Kafka) per tenant.
- Gateway extracts tenant from auth metadata or `X-Tenant` headers.
- Backfill legacy records with `default` tenant and enforce per-tenant quotas.

## 10. Capacity and SLO Targets

- Baseline production goal: 200 effective RPS (mix: 60% local, 30% API, 10% hybrid).
- Latency targets: local ≤ 500 ms (P95), API ≤ 2000 ms, hybrid ≤ 2300 ms.
- Reliability: ≥ 99 % 24h success, ≥ 99.5 % availability.
- Scale via gateway/control plane replication and autoscaling modules.

## 11. Operational Runbook

1. Boot & health: bring up stack (Docker Compose or Kubernetes), verify `/healthz` endpoints.
2. Secrets/keys: provision Vault/SOPS, register provider keys, validate Cosign verification.
3. Policies: load `intents.yml`, `policies.yml`, `models.yml`, `modules.yml`; test overrides.
4. Observability: ensure Prometheus/Grafana active; validate OTEL traces.
5. Kafka: create topics with partitions, enable ACLs, test producers/consumers.
6. Modules: install packages via `aionctl`, run smoke tests.
7. Rollback: maintain A/B versions for policies; enable router rollback via `/router/policy/reload`.
8. Incident response: activate circuit breakers, adjust routing tiers, throttle module parallelism, enable `local-only` mode as needed.

## 12. Testing and Acceptance Criteria

- Contract validation for JSON schemas and protobuf definitions.
- Functional coverage of local/API/hybrid flows, streaming, and cancellation propagation.
- Load tests at 200 RPS with varied inputs, observing backpressure and queue limits.
- Chaos scenarios: provider latency/outage, module crashes, interrupted streaming.
- Security validation: RBAC/ABAC enforcement, injection testing, log redaction, package signing, non-root execution.
- Big data pipeline checks: Kafka → ClickHouse/MinIO ingestion → Superset dashboards.

## 13. Sample Policy and Registry Files

### intents.yml

```yaml
summarize:
  default_route: auto
  candidates: [local, api, hybrid]
  privacy: allow-api
  tiers_allowed: [tier0, tier1]
  vector_usage: false

invoice_ocr:
  default_route: hybrid
  candidates: [local, hybrid]
  privacy: local-only
  tiers_allowed: [tier0]
  vector_usage: true
```

### policies.yml

```yaml
budget:
  default_usd: 0.02
  hard_cap_usd: 0.20
latency:
  p95_ms:
    local: 600
    api: 2000
    hybrid: 2300
privacy:
  local_only_intents: ["invoice_ocr"]
providers:
  deny: []
  allow: ["ollama", "openai", "azure", "hf", "vllm"]
routing:
  fallback_order: ["local", "api", "hybrid"]
```

### models.yml

```yaml
tiers:
  tier0:
    local: ["ollama:qwen2.5", "vllm:llama3.1"]
  tier1:
    cloud: ["openai:gpt-4.1-mini", "azure:gpt-4o-mini", "hf:mistral-large"]
  tier2:
    cloud: ["openai:gpt-4.1", "azure:gpt-4o", "hf:mixtral-8x22b"]
```

### modules.yml

```yaml
modules:
  - name: summarize_text
    ref: "ghcr.io/aion/summarize_text:1.3.0"
    runtime: wasm
    signatures: ["cosign:..."]
    timeout_ms: 1500
    limits: { cpu: "0.5", memory: "256Mi" }
```

## 14. Key Sequences

### Task Creation (Auto Route)

1. Client submits `/v1/tasks` with JWT and `Idempotency-Key`.
2. Gateway forwards to control plane over REST/gRPC.
3. Control validates, extracts features, consults router for a decision.
4. Control dispatches to the selected engine, collects results, and normalizes the response.
5. Control emits metrics and Kafka events before replying (REST/stream updates).
6. Client consumes partials via WS/SSE until the final result arrives.

### Policy Reload

1. Data team trains/tunes policy via big data pipeline.
2. Store new version in MinIO (`aion-models/`) and registry.
3. Call `/router/policy/reload`; control plane loads the new version and logs activity.

## 15. Rate-Limiting and Idempotency

- Redis-backed token buckets: e.g., 60 RPM (burst 120) per API key, 120 RPM per IP.
- Idempotency keys cached for 5–15 minutes to avoid duplicate charges or repeated provider calls.

## 16. Deployment Paths

### 16.1 Docker Compose (Dev/MVP)

- Services: gateway, control, Postgres, Redis, Qdrant, MinIO, Kafka, optional Ollama/vLLM, Superset, ClickHouse, Spark.
- Use dedicated networks (`aion-core-net`, `aion-bigdata-net`) and persistent volumes.

### 16.2 Kubernetes (Prod)

- Separate deployments with HPAs driven by CPU/RPS/latency.
- Service mesh for mTLS and network policy enforcement.
- Use Secrets/ConfigMaps for configuration and keys.
- Ingress with WAF and specialized GPU/CPU node pools.

## 17. Delivery Checklist

- JSON schema and proto files with positive/negative samples.
- Sample WASM and subprocess AIP packages.
- Policy/registry files and `aionctl` tooling.
- Prebuilt Grafana/Superset dashboards.
- Smoke test scripts (HTTP/gRPC/WS + Kafka publish).
- Runbook covering boot, health, rotation, backup, incident, rollback.
- Security profiles (seccomp/AppArmor) and cgroup settings documentation.

