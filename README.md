# aionOS

aionOS is a modular AI orchestration platform combining a TypeScript gateway, FastAPI control plane, and Rust execution modules. It embraces WASM-first execution, policy-driven routing, and production-grade observability.

## Features

- Gateway with REST, gRPC, SSE, and WebSocket APIs
- FastAPI control plane with policy-aware routing, cost metering, and storage connectors
- Rust modules supporting WASM and subprocess execution paths
- Kafka streaming pipelines with Spark and Airflow orchestration
- ClickHouse analytics, MinIO object storage, and Superset dashboards
- Cosign signing, SBOM generation, and comprehensive CI/CD

## Quick Start (Docker Compose)

```bash
cp .env.example .env
cp .env.bigdata.example bigdata/.env
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

| Component | Variable | Description |
|-----------|----------|-------------|
| Gateway | `AION_GATEWAY_PORT` | HTTP listen port |
| Gateway | `AION_CONTROL_GRPC` | Control plane gRPC endpoint |
| Gateway | `AION_GATEWAY_API_KEYS` | Comma separated `key:role1|role2[:tenant]` |
| Gateway | `AION_RATE_LIMIT_MAX` / `AION_RATE_LIMIT_PER_IP` | Per-key and per-IP request ceilings |
| Gateway | `AION_TLS_CERT` / `AION_TLS_KEY` | TLS certificate paths for production |
| Control | `AION_CONTROL_REDIS_URL` | Redis connection string |
| Control | `AION_CONTROL_POSTGRES_DSN` | PostgreSQL DSN |
| Control | `AION_CONTROL_MONGO_DSN` | Mongo connection string |
| Control | `TENANCY_MODE` | `single` or `multi` to enforce tenant headers |
| Console | `NEXTAUTH_URL` / `NEXTAUTH_SECRET` | Auth callback URL and signing secret |
| Console | `NEXT_PUBLIC_GATEWAY_URL` | Base URL for REST/SSE calls |
| Console | `NEXT_PUBLIC_CONTROL_URL` | Base URL for control-plane APIs |
| Console | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth credentials for Google login |
| Big Data | `KAFKA_BROKERS` | Kafka bootstrap servers |
| Big Data | `CLICKHOUSE_URL` | ClickHouse endpoint |

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

The Glass UI console lives under `/console`. Run `pnpm install && pnpm dev` to start the Next.js dev server with live task streaming, policy editing, and RTL support.

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
