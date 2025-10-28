# aionOS (Agent-OS) — AIONOS Branch

aionOS is a modular AI orchestration platform that combines a **TypeScript Gateway**, a **FastAPI Control Plane**, and **Rust/WASM execution modules**. It focuses on policy-driven routing, local-first privacy modes, and production-grade observability.  
**License:** Apache-2.0

> This README describes the **native (no-Docker)** developer setup for Ubuntu/Debian. A Docker Compose path may also exist, but the recommended route here is **from source**.

---

## ✨ Key Features
- **Gateway (Fastify/TypeScript):** REST + SSE/WS + (optional) gRPC, API-keys, rate-limit, idempotency, OTEL propagation.
- **Control (FastAPI/Python):** AI decision router, task orchestration, pluggable providers (OpenAI/Azure/HF/vLLM/Ollama), storage connectors (PostgreSQL/MongoDB/Redis/Qdrant).
- **Modules (Rust/WASM/Subprocess):** Safe execution with policy manifests, optional Cosign/SBOM for supply-chain integrity.
- **Data & Observability:** Kafka/ClickHouse/Spark/Airflow (optional), MinIO object storage, OTEL tracing, Prometheus metrics.

---

## 🗺️ Architecture (high-level)

```mermaid
flowchart LR
  U[Client / Console] -- REST/SSE/WS --> G[Gateway (Fastify)]
  G -- gRPC/REST --> C[Control (FastAPI)]
  C -- gRPC/IPC/WASM --> M[Modules (Rust/WASM/Subprocess)]
  C -- drivers --> D[(Datastores: Postgres/Mongo/Redis/Qdrant/MinIO)]
  C <-- events --> K[(Kafka)]
  subgraph Observability
    G -. OTEL .-> O[(Collector)]
    C -. OTEL .-> O
  end
```

⸻

🧰 Requirements (native)
•OS: Ubuntu 22.04+ / Debian 12+ (tested)
•Node.js: v20.x (use nvm)
•Python: 3.11+
•Rust: stable (for module dev)
•Datastores (choose what you need):
•Redis 7+, PostgreSQL 14+/MongoDB 6+, Qdrant (optional), MinIO (optional)

⸻

⚡ Quick Start (native, no Docker)

Create a clean workspace terminal and run the following:

```
# 1) System deps
sudo apt update
sudo apt install -y build-essential curl git python3.11 python3.11-venv python3-pip \
                     redis-server pkg-config libssl-dev

# 2) Node 20 via nvm
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm" && . "$NVM_DIR/nvm.sh"
nvm install 20 && nvm use 20

# 3) Clone AIONOS branch
git clone -b AIONOS --single-branch https://github.com/ghasemzadeh-hamed/OMERTAOS.git
cd OMERTAOS

# 4) Gateway (TypeScript)
cd gateway
npm ci
cp .env.example .env
# minimal env for dev:
# AION_GATEWAY_PORT=8080
# AION_CONTROL_GRPC=localhost:50051
# AION_GATEWAY_API_KEYS=dev-key:admin
npm run dev
# (keep running; in a new terminal continue)

# 5) Control (FastAPI)
cd ../control
python3.11 -m venv .venv && source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
cp .env.example .env
# minimal env for dev:
# AION_CONTROL_REDIS_URL=redis://localhost:6379
# TENANCY_MODE=single
uvicorn app.main:app --host 0.0.0.0 --port 50052 --reload
# OR if gRPC sidecar is used, run it per repo instructions

# 6) (Optional) Console
cd ../console
npm ci
cp .env.local.example .env.local
npm run dev
```

Verify health
•Gateway: http://localhost:8080/healthz
•Control: http://localhost:50052/healthz (or the configured port)

First admin / API key

For development, the Gateway reads AION_GATEWAY_API_KEYS. Example in .env:

```
AION_GATEWAY_API_KEYS=dev-key:admin|manager
```

Submit a task

```
curl -X POST "http://localhost:8080/v1/tasks" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "schemaVersion": "1.0",
    "intent": "summarize",
    "params": {"text": "Hello aionOS"}
  }'
```

Stream output (SSE)

```
curl -N "http://localhost:8080/v1/stream/<TASK_ID>" -H "X-API-Key: dev-key"
```

⸻

🔧 Configuration Matrix (common)

| Component | Variable | Description |
|-----------|----------|-------------|
| Gateway | AION_GATEWAY_PORT | HTTP listen port (default: 8080) |
| Gateway | AION_CONTROL_GRPC | Control plane gRPC/REST endpoint |
| Gateway | AION_GATEWAY_API_KEYS | Comma-separated `key:role1\|role2` pairs |
| Gateway | AION_RATE_LIMIT_* | Per-key/IP throttling |
| Gateway | AION_TLS_CERT/AION_TLS_KEY | TLS in production |
| Control | TENANCY_MODE | single or multi (tenant headers enforced) |
| Control | AION_CONTROL_REDIS_URL | Redis URL |
| Control | AION_CONTROL_POSTGRES_DSN | Postgres DSN (optional) |
| Control | AION_CONTROL_MONGO_DSN | Mongo DSN (optional) |
| Providers | see policies/*.yml | Provider configs and allowlists |
| Console | NEXT_PUBLIC_GATEWAY_URL | Base URL for REST/SSE |
| Console | NEXTAUTH_* | If SSO/OAuth is enabled |

Policies live in /policies (intents.yml, models.yml, modules.yml, policies.yml).
Reload via Control API (POST /v1/router/policy/reload).

⸻

📁 Project Layout

```
.github/workflows   CI/CD, scans, SBOM
bigdata/            Kafka/ClickHouse/Spark/Airflow (optional)
console/            Next.js admin console
control/            FastAPI control plane
gateway/            Fastify/TypeScript gateway
kernel/             Core abstractions
modules/            Rust/WASM/subprocess modules + manifests
policies/           intents/models/modules/policies
protos/aion/v1/     gRPC definitions
schemas/            JSON/YAML schemas
scripts/            helper scripts
tests/              e2e/integration tests
```

⸻

🔐 Security
•Secrets via environment or your vault (no secrets in git).
•Production behind a TLS reverse-proxy; enable rate-limit and idempotency.
•Use GitHub private vulnerability reporting (see SECURITY.md).

⸻

🧭 Roadmap (short)
•Multi-tenant auth with OIDC (optional)
•Pluggable provider registry UI
•Module Store + signatures (Cosign)
•More built-in policies for low-latency local routing

⸻

🤝 Contributing

See CONTRIBUTING.md and follow Conventional Commits.
