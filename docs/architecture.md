# OMERTAOS Reference Architecture

This document consolidates the end-to-end guidance for implementing the OMERTAOS
platform. It reframes the original strategy into a navigable reference so that
engineering, data, and operations teams can align on scope, responsibilities,
and execution.

## 0. Strategic Summary (What & Why)

* **Tenancy** – Begin single-tenant, but model data and tokens with a
  future-proof `tenant_id` so that multi-tenant roll-out requires no breaking
  changes.
* **AuthN/Z** – API Key or JWT for the first phase; offer OIDC/SSO extensions.
  Combine RBAC and ABAC through a central policy engine. Keep tokens short-lived
  with rotation.
* **Execution** – Prefer WASM for isolation and portability. Allow hardened
  subprocesses when native acceleration or OS capabilities are required.
  Distribute packages as OCI/ORAS artifacts with mandatory Cosign signatures and
  SBOM publication.
* **Accelerators** – Provide first-class support for NVIDIA CUDA/cuDNN, AMD
  ROCm, and Intel oneAPI/Level-Zero. Capture GPU policy inside the AIP manifest.
* **Data & Streams** – Use Postgres plus Mongo for metadata and structured logs,
  Kafka for events, Qdrant for vector storage, and MinIO for objects.
* **Interfaces** – Support REST, WebSockets/SSE, and public gRPC (alongside the
  internal gRPC). Adopt schema-first design and version APIs.
* **Residency & Privacy** – Offer policy-driven residency without mandatory
  restrictions. Support `local-only`, `allow-api`, and `hybrid` modes.
* **Model Providers** – Allow all providers with tier-based defaults that map to
  local, cost-optimised, and high-intelligence options per intent.

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

**Key Principles**

* The **Gateway** handles edge concerns (auth, rate limits, TLS, streaming,
  idempotency) and defers business logic to the control plane.
* The **Control Plane** owns routing, orchestration, policy enforcement, memory
  services, and cost metering.
* **Modules** default to WASM (WASI) with subprocesses reserved for cases where
  hardware or system-level calls are required.
* The **Big Data** stack is Kafka-centric for decisions, tasks, metrics, and
  audit records, with Spark/Flink processing, ClickHouse warehousing, and MinIO
  as the object lake.

## 2. Module Execution Model

### 2.1 AIP Manifest (Example)

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

### 2.2 WASM Execution

* Use wasmtime or wasmedge with WASI support.
* Restrict hostcalls to essentials such as clock, random, and logging.
* Enable network access strictly via manifest permissions.
* Pass request context as JSON over stdin or an in-process gRPC ABI.

### 2.3 Subprocess Execution

* Reserve for GPU workloads, specialised system calls, or libraries that cannot
  target WASM.
* Enforce sandboxing with non-privileged users, seccomp/AppArmor, cgroups, and
  read-only filesystems.
* Prefer JSON over stdio or gRPC loopback for I/O contracts.

### 2.4 Distribution & Installation

* Use ORAS/OCI to distribute packages and Cosign for mandatory signature
  verification.
* Publish SBOM artifacts and quarantine packages that fail validation.

## 3. API Contracts

### 3.1 REST (Gateway)

* `POST /v1/tasks` – Submits tasks with JWT/API key auth, idempotency key, and
  trace context.
* `GET /v1/tasks/{task_id}` – Returns status and results.
* `GET /v1/stream/{task_id}` – Streams partial outputs over SSE/WS.

All responses share a canonical result envelope including status, engine
metadata, usage, and error details when applicable.

### 3.2 Public gRPC

The `aion.v1` service exposes `Submit`, `Stream`, and `StatusById` RPCs with
schema-first design, mTLS, and JWT metadata. Fields are additive for
forward-compatible evolution.

### 3.3 WS/SSE

WebSocket endpoint `/v1/ws` uses an operation-based contract, while SSE follows
standard event naming (`token`, `partial`, `done`, `error`).

## 4. AI Decision Router

* Providers are grouped into tiers (local, cloud-standard, cloud-premium).
* Routing considers intent privacy, budget, latency, payload features, and
  policy overrides.
* A dedicated prompt instructs the router to return structured decisions.
* Fallbacks prefer safe defaults when routing fails.

## 5. Data & Storage Strategy

* **Postgres** – Core tables (`agents`, `tasks`, `policies`, `modules`,
  `models`, `usage_billing`, `audit_activity`), all ready for future `tenant_id`
  columns.
* **Mongo** – Optional structured log store with TTL policies.
* **Kafka** – Mandatory backbone with topics for routing decisions, task
  lifecycle, runtime metrics, and audit logs. Secure with SASL/SCRAM or mTLS and
  ACLs.
* **Qdrant** – Vector embeddings organised per tenant.
* **MinIO/S3** – Buckets for raw, processed, feature, and model assets with
  lifecycle rules.

## 6. Observability & Retention

* OpenTelemetry tracing across gateway, control plane, and modules.
* Prometheus metrics for performance, queue depth, GPU utilisation, and
  streaming backpressure.
* Grafana dashboards covering routing, task health, and resource utilisation.
* Log retention policies: 7–14 days for development, 30–90 days for production
  with TTL enforcement.

## 7. Security & Governance

* API keys for machine-to-machine, short-lived JWTs for users, OIDC as an
  extension.
* RBAC plus ABAC to manage intent, provider, and tenant constraints.
* Secrets managed via Vault/SOPS with enforced rotation.
* PII protection through log masking and privacy-aligned routing.
* Supply-chain integrity through Cosign, SBOMs, and container scanning.
* Default deny network posture with allowlists for providers and mandatory rate
  limiting with token buckets.

## 8. Concurrency & Backpressure

* Gateway uses PM2 clusters, manages WS/SSE backpressure, and drains gracefully
  on deploy.
* Control plane employs worker pools, bounded queues, and returns 429/503 with
  `Retry-After` when saturated.
* Modules set per-replica concurrency, cgroup limits, and circuit breakers.

## 9. Migration to Multi-Tenant

* Add `tenant_id` columns and composite indexes to Postgres tables.
* Extend JWT claims and API key scopes with tenant identifiers.
* Namespace external stores (Qdrant, Redis, MinIO, Kafka) by tenant.
* Derive tenant context from auth headers at the gateway.
* Backfill existing data with a `default` tenant and roll out isolation policies.

## 10. Capacity & SLO Targets

* Baseline production: 200 RPS mix (60% local, 30% API, 10% hybrid).
* Latency targets: ≤500 ms local P95, ≤2000 ms API P95, ≤2300 ms hybrid P95.
* Availability: ≥99.5% with ≥99% successful completions per 24 hours.

## 11. Operational Runbook

1. Boot core services (`docker compose up` for dev or Kubernetes in prod) and
   verify `/healthz` endpoints.
2. Provision secrets, register provider keys, and validate Cosign verification.
3. Load policies and registries (`intents.yml`, `policies.yml`, `models.yml`,
   `modules.yml`).
4. Bring up observability (Prometheus, Grafana) and validate OTEL traces.
5. Configure Kafka topics with partitions, ACLs, and smoke-test producers and
   consumers.
6. Install sample AIP packages via `aionctl install` and run smoke tests.
7. Prepare rollback procedures for policies and router models.
8. Respond to incidents with circuit breakers, tier overrides, or reduced
   parallelism.

## 12. Testing & Acceptance

* Contract testing for JSON schemas and protobuf definitions.
* Functional coverage for routing modes, streaming, and cancellation paths.
* Load testing at 200 RPS including backpressure scenarios.
* Chaos tests simulating provider degradation, module crashes, and stream
  interruptions.
* Security validation for authz flows, log hygiene, signature checks, and
  non-root enforcement.
* Big data validation from Kafka publication through analytics dashboards.

## 13. Policy & Registry Samples

See the canonical examples below for intents, policies, models, and module
registry entries.

```yaml
# intents.yml
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

```yaml
# policies.yml
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
  allow: ["ollama","openai","azure","hf","vllm"]
routing:
  fallback_order: ["local","api","hybrid"]
```

```yaml
# models.yml
tiers:
  tier0:
    local: ["ollama:qwen2.5","vllm:llama3.1"]
  tier1:
    cloud: ["openai:gpt-4.1-mini","azure:gpt-4o-mini","hf:mistral-large"]
  tier2:
    cloud: ["openai:gpt-4.1","azure:gpt-4o","hf:mixtral-8x22b"]
```

```yaml
# modules.yml
modules:
  - name: summarize_text
    ref: "ghcr.io/aion/summarize_text:1.3.0"
    runtime: wasm
    signatures: ["cosign:..."]
    timeout_ms: 1500
    limits: { cpu: "0.5", memory: "256Mi" }
```

## 14. Key Sequences

### 14.1 Create Task (Auto Route)

1. Client calls `POST /v1/tasks` with JWT and idempotency key.
2. Gateway forwards to control plane via REST/gRPC.
3. Control plane validates, builds features, invokes router, and selects a
   route.
4. Control plane dispatches to the chosen execution path, gathers the result,
   and normalises the response envelope.
5. Metrics and Kafka events are emitted before the gateway responds and streams
   updates.
6. Client receives partials over WS/SSE and the final canonical result.

### 14.2 Policy Reload

1. Data team trains or updates policies via the big data pipeline.
2. The new version is stored in MinIO and registered.
3. `POST /router/policy/reload` triggers the control plane to load the new
   version and emit activity logs.

## 15. Rate Limiting & Idempotency

* Redis-backed token buckets: 60 requests per minute per API key (burst 120) and
  120 rpm per IP.
* Idempotency keys cache responses for 5–15 minutes to prevent duplicate work or
  charges.

## 16. Deployment Paths

### 16.1 Docker Compose (Dev/MVP)

* Services: gateway, control, postgres, redis, qdrant, minio, kafka, plus
  optional ollama, vllm, superset, clickhouse, spark.
* Use dedicated networks for core services and big data components, with
  persistent volumes for stateful workloads.

### 16.2 Kubernetes (Prod)

* Deploy each service independently with HPA policies (CPU/RPS/latency).
* Employ a service mesh for mTLS and network policy enforcement.
* Manage secrets and configuration via Secrets/ConfigMaps.
* Provide ingress with WAF and dedicated GPU/CPU node pools.

## 17. Delivery Checklist

* JSON schemas, proto files, and sample payloads (valid/invalid).
* WASM and subprocess AIP packages.
* Policy and registry files validated with `aionctl`.
* Grafana and Superset dashboards ready for import.
* Smoke-test scripts for HTTP, gRPC, WS, and Kafka workflows.
* Runbooks covering boot, health, rotation, backup, incidents, and rollback.
* Seccomp/AppArmor profiles and cgroup configurations documented.
