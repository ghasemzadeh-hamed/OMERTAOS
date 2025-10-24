# aionOS

aionOS is a modular AI orchestration platform combining a TypeScript gateway, FastAPI control plane, and Rust execution modules. It embraces WASM-first execution, policy-driven routing, and production-grade observability.

## Features

- Gateway with REST, gRPC, SSE, and WebSocket APIs
- FastAPI control plane with policy-aware routing, cost metering, and storage connectors
- Rust modules supporting WASM and subprocess execution paths
- Kafka streaming pipelines with Spark and Airflow orchestration
- ClickHouse analytics, MinIO object storage, and Superset dashboards
- Cosign signing, SBOM generation, and comprehensive CI/CD
- Admin-gated kernel automation with proposal approvals, TTL/canary rollback, and signed webhooks
- Next.js Glass UI console featuring bilingual ChatOps terminal, live policy editing, and telemetry embeds

## Quick Start (Docker Compose)

```bash
cp .env.example .env
cp .env.bigdata.example bigdata/.env
cp console/.env.local.example console/.env.local
./scripts/dev-up.sh
```

Expose the gateway on `http://localhost:8080` and the console on `http://localhost:3000`. Health checks are available at `/healthz` for both gateway and control services.

### First Admin Creation

Create the first API key by exporting `AION_GATEWAY_API_KEYS` in `.env`:

```
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

### Submitting a Task

```bash
curl -X POST http://localhost:8080/v1/tasks \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key" \
  -d '{
    "schemaVersion": "1.0",
    "intent": "summarize",
    "params": {"text": "hello world"}
  }'
```

Follow the task stream via SSE:

```bash
curl http://localhost:8080/v1/stream/<task_id> -H "X-API-Key: demo-key"
```

### gRPC Example

```
grpcurl -plaintext -d '{"schema_version":"1.0","intent":"summarize","params":{"text":"hi"}}' localhost:50051 aion.v1.AionTasks/Submit
```

## Architecture Overview

- **Gateway**: Fastify-based service providing auth, rate limiting, idempotency, and SSE/WS streaming. Proxies to the control plane via gRPC with OTEL propagation.
- **Control Plane**: FastAPI application with router decision engine, task orchestrator, Kafka events, and persistence connectors (PostgreSQL, MongoDB, Redis, Qdrant).
- **Modules**: Rust implementations delivered as WASM or sandboxed subprocesses. Manifests include Cosign signature metadata, SBOM references, and policy constraints.
- **Data Platform**: Kafka-backed streaming into ClickHouse with Spark, Airflow DAGs for batch processing, and Superset dashboards.

## Configuration Matrix

| Component | Variable | Default | Description |
|-----------|----------|---------|-------------|
| Gateway | `AION_GATEWAY_PORT` | `8080` | HTTP listen port for REST/WS APIs. |
| Gateway | `AION_CONTROL_GRPC` | `control:50051` | Upstream control-plane gRPC endpoint. |
| Gateway | `AION_GATEWAY_API_KEYS` | `demo-key:admin|manager` | Comma separated `key:role1|role2[:tenant]` list for API key auth. |
| Gateway | `AION_RATE_LIMIT_MAX` | `60` | Requests per window per API key. |
| Gateway | `AION_RATE_LIMIT_PER_IP` | `120` | Requests per window per client IP. |
| Gateway | `AION_RATE_LIMIT_PER_USER` | `90` | Requests per window per authenticated user (JWT/API key subject). |
| Gateway | `AION_RATE_LIMIT_WINDOW` | `1 minute` | Token bucket window (supports `s|m|h`). |
| Gateway | `AION_IDEMPOTENCY_TTL` | `900` | TTL seconds for idempotency cache entries. |
| Gateway | `AION_TLS_ENABLED` | `false` | Enables TLS for REST/WS listeners when `true`. |
| Gateway | `AION_TLS_CERT_PATH` / `AION_TLS_KEY_PATH` | _empty_ | Certificate/private key paths for TLS termination. |
| Gateway | `AION_MTLS_ENABLED` | `false` | Require client certificates for public gRPC. |
| Gateway | `AION_TLS_CA_CHAIN` | _empty_ | CA bundle for validating client certs (mTLS) and upstream TLS. |
| Gateway | `AION_OUTBOUND_WEBHOOKS` | `http://localhost:9500/webhook|super-secret|task.status.changed,chat.session.created|3|5` | Semicolon-separated `url|secret|topics|retries|backoff` definitions for outbound hooks. |
| Gateway | `AION_INBOUND_WEBHOOK_SECRET` | `super-secret` | Shared secret for validating inbound webhook signatures. |
| Gateway | `TENANCY_MODE` | `single` | `single` maintains legacy behaviour, `multi` requires tenant headers and namespaces caches. |
| Gateway | `AION_CONSOLE_USERS` | `admin@aionos.dev:changeme:admin|manager` | Seed console credentials in `email:password:role1|role2[:tenant]` form. |
| Gateway | `AION_CONSOLE_GATEWAY_API_KEY` | `demo-key` | API key injected by the console proxy when calling the gateway. |
| Control | `AION_CONTROL_POSTGRES_DSN` | `postgresql://postgres:postgres@postgres:5432/aion` | PostgreSQL connection string for metadata. |
| Control | `AION_CONTROL_REDIS_URL` | `redis://redis:6379/1` | Redis connection (queues, caches). |
| Control | `AION_CONTROL_MONGO_DSN` | `mongodb://mongo:27017/aion` | MongoDB for structured logs. |
| Control | `AION_CONTROL_KAFKA_BROKERS` | `kafka:9092` | Kafka bootstrap servers. |
| Control | `AION_CONTROL_SCHEMA_REGISTRY_URL` | `http://schema-registry:8081` | Confluent Schema Registry endpoint. |
| Control | `MONGO_TTL_DAYS` | `14` | TTL days for dev Mongo collections (prod override to 30-90). |
| Control | `CLICKHOUSE_TTL_DAYS` | `90` | ClickHouse retention window. |
| Console | `NEXTAUTH_URL` / `NEXTAUTH_SECRET` | `http://localhost:3000` / `change-me` | NextAuth configuration for callbacks and signing. |
| Console | `NEXT_PUBLIC_GATEWAY_URL` | `http://localhost:8080` | Gateway origin for proxy routes. |
| Console | `NEXT_PUBLIC_CONTROL_URL` | `http://localhost:8081` | Control plane origin for policy APIs. |
| Console | `CONSOLE_GATEWAY_API_KEY` | `demo-key` | API key forwarded by the console to the gateway. |
| Console | `NEXT_PUBLIC_CONSOLE_GATEWAY_KEY` | `demo-key` | Public-side key embedded for ChatOps proxy requests. |
| Console | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | _empty_ | Optional Google OAuth credentials for SSO. |
| Big Data | `KAFKA_BROKERS` | `kafka:9092` | Kafka bootstrap list for pipelines. |
| Big Data | `SCHEMA_REGISTRY_URL` | `http://schema-registry:8081` | Schema registry used by pipelines and bootstrap script. |
| Big Data | `CLICKHOUSE_URL` | `http://clickhouse:8123` | ClickHouse HTTP endpoint. |
| Big Data | `MINIO_ENDPOINT` | `http://minio:9000` | MinIO endpoint for raw/processed object storage. |

Copy `.env.example` and `bigdata/.env.bigdata.example` as-is for local development; production deployments should supply hardened secrets, TLS assets, and tenant-aware API keys.

Privacy modes (`local-only`, `allow-api`, `hybrid`) are defined per intent in `policies/intents.yml`. Default latency targets (P95) are local ≤ 600 ms, api ≤ 2000 ms, hybrid ≤ 2300 ms. Budgets default to 0.02 USD with a hard cap of 0.20 USD.

## Policies

Policies reside in `/policies`:

- `intents.yml`: routing candidates, privacy, vector usage
- `policies.yml`: latency, budget, provider allowlists
- `models.yml`: provider tiers
- `modules.yml`: registered local modules and manifests

Reload policies via `POST /v1/router/policy/reload` on the control plane.

## Providers & Keys

Store provider credentials in environment variables or secrets stores referenced by policy metadata. Modules declare required secrets in manifests. The platform supports OpenAI, Azure, Hugging Face, vLLM, and Ollama providers. GPU preferences are expressed through module manifests (`resources.gpu`).

## Console

The Glass UI console lives under `/console`. Run `pnpm install && pnpm dev` to start the Next.js dev server with live task streaming, policy editing, RTL support, and the ChatOps terminal. The terminal proxies `/v1/chat/*` endpoints, streams responses via SSE, and honors privacy/engine toggles per command.

## Observability

- **Prometheus** scrapes metrics from gateway, control, and module hosts.
- **Grafana** dashboards reside under `deploy/observability/grafana`.
- **OpenTelemetry** spans propagate trace context between services.

## Testing

- Gateway: `npm test` (Vitest)
- Control: `poetry run pytest`
- Modules: `cargo test`
- End-to-end: `npm run e2e` in `gateway`
- Load: `k6 run tests/load.js`

## Big Data Edition

Bring up analytics services with `docker compose -f bigdata/docker-compose.bigdata.yml up`. Streaming jobs are in `bigdata/pipelines/streaming`, batch DAGs in `bigdata/pipelines/batch/airflow`, and ClickHouse DDL files under `bigdata/sql`.

## Assumptions

- Default environment values target local development; production deployments should supply hardened credentials and TLS.
- Idempotency relies on Redis availability; failures degrade gracefully to non-idempotent behavior.
- gRPC communication currently uses insecure transport in dev; production must enable mTLS.

## License

Apache-2.0 — see [LICENSE](LICENSE).
