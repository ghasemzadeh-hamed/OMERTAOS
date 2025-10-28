# AION-OS (Agent Web-OS) — Modular, Distributed AI Agent Operating System
[FA ⭢ فارسی](#-معرفی-فارسی) · [EN ⭢ English](#-english-overview)

AION-OS is a **modular AI orchestration platform** with a multi-plane architecture:
**Gateway (TypeScript/Fastify)**, **Control (FastAPI)**, **Execution Modules (Rust/WASM)**, and a **Glass-UI Console (Next.js)**.
It ships policy-driven routing, streaming (SSE/WS), analytics pipelines, and production-grade observability.  
[oai_citation:1‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)

---

## ✨ Features
- **Gateway:** REST, gRPC, SSE & WebSocket APIs; auth, rate-limit, idempotency; OTEL propagation to Control.  
  [oai_citation:2‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)
- **Control Plane (FastAPI):** policy-aware router, task orchestrator, Kafka events; Postgres/Mongo/Redis/Qdrant connectors.  
  [oai_citation:3‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)
- **Modules (Rust):** WASM-first or sandboxed subprocess; Cosign signature, SBOM metadata, policy constraints.  
  [oai_citation:4‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)
- **Data Platform:** Kafka→ClickHouse with Spark; Airflow DAGs; Superset dashboards.  
  [oai_citation:5‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)
- **Security & CI/CD:** Cosign signing, SBOM, comprehensive GitHub Actions pipeline.  
  [oai_citation:6‡GitHub](https://github.com/ghasemzadeh-hamed/OMERTAOS/tree/AIONOS)

---

## 🚀 Quick Start (Docker Compose)
```bash
cp .env.example .env
cp .env.bigdata.example bigdata/.env
./scripts/dev-up.sh
```

Then open Gateway at http://localhost:8080 and Console at http://localhost:3000. Health checks are at /healthz for gateway & control.  

**First Admin API Key**

Add to `.env` (comma-separated for multiple keys/roles):

```
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

**Submit a Task (REST)**

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

**Follow live events via SSE:**

```bash
curl http://localhost:8080/v1/stream/<task_id> -H "X-API-Key: demo-key"
```

**gRPC example:**

```bash
grpcurl -plaintext \
  -d '{"schema_version":"1.0","intent":"summarize","params":{"text":"hi"}}' \
  localhost:50051 aion.v1.AionTasks/Submit
```

---

## 🧱 Repository Structure
```
.bigdata/      # analytics stack: Kafka, Spark, ClickHouse, Airflow, Superset
console/       # Next.js Glass UI (task streaming, policy editing, RTL)
control/       # FastAPI: router, orchestrator, events, persistence
gateway/       # TypeScript Fastify service (REST/gRPC/SSE/WS, auth, rate-limit)
modules/       # Rust modules (WASM/subprocess) + manifests/signing
policies/      # intents.yml, policies.yml, models.yml, modules.yml
deploy/        # observability: Prometheus/Grafana
scripts/       # dev & ops scripts (e.g., dev-up.sh)
docs/ tests/ protos/ schemas/ kernel/
```
(See repo root for the full list.)

---

## ⚙️ Configuration (env matrix — key vars)
- **Gateway:** `AION_GATEWAY_PORT`, `AION_CONTROL_GRPC`, `AION_GATEWAY_API_KEYS`, `AION_RATE_LIMIT_MAX`, `AION_RATE_LIMIT_PER_IP`, `AION_TLS_CERT`, `AION_TLS_KEY`
- **Control:** `AION_CONTROL_REDIS_URL`, `AION_CONTROL_POSTGRES_DSN`, `AION_CONTROL_MONGO_DSN`, `TENANCY_MODE` (single|multi)
- **Console:** `NEXTAUTH_URL`, `NEXTAUTH_SECRET`, `NEXT_PUBLIC_GATEWAY_URL`, `NEXT_PUBLIC_CONTROL_URL`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- **Big Data:** `KAFKA_BROKERS`, `CLICKHOUSE_URL`

Privacy modes per intent: `local-only | allow-api | hybrid`. Default P95 targets and budget caps are defined in policies.

---

## 📜 Policies & Live Reload

All policies live under `/policies` (`intents.yml`, `policies.yml`, `models.yml`, `modules.yml`).
Reload at runtime: `POST /v1/router/policy/reload` (Control Plane).

---

## 📊 Big Data Edition

Spin up analytics:

```bash
docker compose -f bigdata/docker-compose.bigdata.yml up
```

Streaming jobs: `bigdata/pipelines/streaming/` • Batch: `bigdata/pipelines/batch/airflow/` • ClickHouse DDL: `bigdata/sql/`.

---

## 🔭 Observability
- Prometheus scrapes gateway, control, modules; OpenTelemetry traces across services.
- Grafana dashboards under `deploy/observability/grafana`.

---

## 🧪 Testing
- **Gateway:** `npm test` (Vitest)
- **Control:** `poetry run pytest`
- **Modules:** `cargo test`
- **End-to-end:** `npm run e2e` (gateway)
- **Load:** `k6 run tests/load.js`

---

## 🔐 Security Notes
- Dev uses plaintext gRPC by default — enable mTLS in production.
- Idempotency relies on Redis; in outages, degrades gracefully to non-idempotent behavior.
- Provide hardened secrets & TLS in production.

---

## 📝 License

Apache-2.0. See `LICENSE`.

---

## 🇮🇷 معرفی فارسی

AION-OS یک پلتفرم ارکستراسیون عامل‌های هوش مصنوعی با معماری چندلایه است:
Gateway (TypeScript/Fastify)، Control (FastAPI)، Modules (Rust/WASM) و کنسول Next.js.
پروژه شامل مسیریابی مبتنی بر سیاست، استریم زنده (SSE/WS)، پایپلاین‌های تحلیلی و مشاهده‌پذیری تولیدی است.

### ویژگی‌ها
- APIهای REST/gRPC/SSE/WS، احراز هویت، Rate-Limit و Idempotency در Gateway؛ اتصال OTEL به Control.
- Router و Orchestrator در Control با اتصال به Postgres/Mongo/Redis/Qdrant و انتشار رویدادهای Kafka.
- ماژول‌های Rust به‌صورت WASM یا Subprocess با امضا/سیاست و SBOM.
- داده: Kafka→ClickHouse، Spark، Airflow، داشبوردهای Superset.

### شروع سریع (Compose)

```bash
cp .env.example .env
cp .env.bigdata.example bigdata/.env
./scripts/dev-up.sh
```

- Gateway: http://localhost:8080 • Console: http://localhost:3000 • Health: `/healthz`

**ایجاد کلید ادمین:**

```
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

ارسال Task (REST) و استریم SSE و نمونه gRPC در بالا آمده‌اند.

### سیاست‌ها و ریلود

فایل‌های سیاست در `policies/` و ریلود با `POST /v1/router/policy/reload`.

### مشاهده‌پذیری و تست

Prometheus/Grafana/OTEL آماده؛ تست‌ها و مسیرهای e2e/load مشخص شده‌اند.

### مجوز

Apache-2.0.

---

اگه بخوای، هم‌زمان **Badge**‌های آماده (CI، License) هم به بالای README اضافه می‌کنم، یا بخش «From Source (Dev)» رو هم بر اساس اسکریپت‌های فعلی گسترش می‌دم—بگو تمرکزت روی Dev محلیه یا فقط Compose.
