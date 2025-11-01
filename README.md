# AION-OS (Agent Web-OS)

Build, route, and scale AI agents with a production-ready operating system. AION-OS ships with a modular kernel, privacy-first policy router, and a real-time Glass UI so teams can ship and manage agents anywhere.

[FA ⭢ فارسی](#-معرفی-فارسی)

---

## Contents
- [Overview](#overview)
- [Architecture Highlights](#architecture-highlights)
- [Quick Start (Docker Compose)](#quick-start-docker-compose)
- [Local LLM Options](#local-llm-options)
- [Agent & Console Experiences](#agent--console-experiences)
- [Knowledge & RAG Demo](#knowledge--rag-demo)
- [Observability & Big-Data](#observability--big-data)
- [Testing Matrix](#testing-matrix)
- [Repository Layout](#repository-layout)
- [Security & Privacy](#security--privacy)
- [Roadmap](#roadmap)
- [License](#license)

---

## Overview
AION-OS is a **kernel-style, distributed OS for AI agents**. It combines a secure routing plane, WASM-enabled execution modules, and a bilingual (FA/EN) Next.js console. The system keeps policies, budgets, and knowledge models in sync so agent workflows remain auditable and reproducible.

Key capabilities include:

- **Multi-plane architecture**: Gateway (TypeScript/Fastify), Control (FastAPI), Execution (Rust/WASM), Console (Next.js) for clean separation of concerns.
- **Policy-aware routing**: `local | api | hybrid` runtime selection with per-intent budgets, SLAs, and live reload support.
- **Spec-driven delivery**: repo-level standards under `.aionos/` keep planning, implementation, testing, and documentation aligned for every agent.
- **Knowledge OS**: a project memory graph with citations exposed in the UI and secure IDE/MCP tool hooks.
- **Realtime operations**: WebSocket/SSE streams for tasks, presence, health, and audit events.
- **Defense in depth**: RBAC, API keys/OIDC, sandboxed modules, signed manifests, SBOM generation, and privacy policies per intent.

---

## Architecture Highlights
```
gateway/    Fastify router exposing REST/gRPC/SSE/WS with auth, quotas, idempotency
control/    FastAPI orchestration, policy & budget management, storage adapters
modules/    Rust/WASM execution units with signing and sandboxing
console/    Next.js Glass UI (RTL-ready) with NextAuth, task board, live logs
.aionos/    Spec contracts that guide agents (/plan → /doc) with guardrails
policies/   Intents, model routing, module manifests, privacy definitions
bigdata/    Kafka → ClickHouse, Spark/Flink, Airflow, Superset overlays
```

Supporting directories include `deploy/` for Prometheus, Grafana, and OTel configs, `docs/` for runbooks and diagrams, and `tests/` for unit/e2e/load profiles.

---

## Quick Start (Docker Compose)
```bash
# 1) Clone the AIONOS branch
git clone -b AIONOS --single-branch https://github.com/ghasemzadeh-hamed/OMERTAOS.git
cd OMERTAOS

# 2) Prepare environment files
cp .env.example .env
cp console/.env.example console/.env
cp control/.env.example control/.env

# 3) Launch the core stack
docker compose up -d

# Optional: enable the analytics overlay
docker compose -f bigdata/docker-compose.bigdata.yml up -d
```

Once the containers are healthy:
- Console → `http://localhost:3000`
- Gateway → `http://localhost:8080`
- Health endpoints → append `/healthz`

Use the example admin key for experiments:
```env
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

Trigger a task via REST:
```bash
curl -X POST http://localhost:8080/v1/tasks \
  -H "X-API-Key: demo-key" -H "Content-Type: application/json" \
  -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"Hello AION-OS!"}}'
```

Follow live SSE events:
```bash
curl -H "X-API-Key: demo-key" http://localhost:8080/v1/stream/<task_id>
```

---

## Local LLM Options
### Default (Ollama)
```bash
./install.sh
# Opens http://localhost:3000 (onboarding chat)
# Local LLM runs at http://127.0.0.1:11434
# Override via AIONOS_LOCAL_MODEL="llama3.2:8b" ./install.sh
```

### GPU (vLLM)
Requirements: NVIDIA driver, NVIDIA Container Toolkit, optional `HF_TOKEN`.
```bash
docker compose -f docker-compose.yml -f docker-compose.vllm.yml up -d --build
# OpenAI-compatible endpoint → http://localhost:8008/v1/chat/completions
```

### Switching Engines
Update `config/aionos.config.yaml`:
```yaml
models:
  provider: local
  local:
    engine: vllm   # ollama | vllm
    model: Qwen/Qwen2.5-7B-Instruct
```

---

## Agent & Console Experiences
- **Agent mode demo**: Visit `/agent` on the Console. Configure `NEXT_PUBLIC_CONTROL_BASE` and `NEXT_PUBLIC_AGENT_API_TOKEN`. Optional env overrides: `AIONOS_LOCAL_MODEL`, `OLLAMA_HOST`, `VLLM_HOST`.
- **Onboarding chat**: `http://localhost:3000/onboarding` seeds the initial admin, model provider, and gateway options (Persian chat wizard). Backend routes live under `/admin/onboarding/*` on the control plane.
- **Security tips**: Guard `/agent/*` & `/admin/onboarding/*` with authentication or private networking. Store secrets with Docker/K8s secrets or SOPS/Vault.
- **Smoke test**: After the stack is running, execute `./scripts/smoke_e2e.sh` to probe health, agent, and RAG endpoints.

---

## Knowledge & RAG Demo
Ingest Markdown/plaintext into Qdrant:
```bash
curl -F "col=aionos-docs" -F "files=@README.md" http://localhost:8000/rag/ingest
```

Query the collection:
```bash
curl -X POST http://localhost:8000/rag/query \
  -H "content-type: application/json" \
  -d '{"collection":"aionos-docs","query":"What is AION-OS?","limit":3}'
```

---

## Observability & Big-Data
- **Tracing & metrics**: OpenTelemetry instrumentation with Prometheus exporters and curated Grafana dashboards.
- **Pipeline overlay** (optional): Kafka → ClickHouse ingestion, Spark/Flink jobs, Airflow DAGs, and Superset BI dashboards.

---

## Testing Matrix
- Gateway → `npm test` (Vitest)
- Control → `pytest`
- Modules → `cargo test`
- Console → Playwright e2e suite
- Load → `k6` profiles

---

## Repository Layout
```
policies/   Intent routing, model configs, module manifests, privacy rules
deploy/     K8s manifests, Prometheus/Grafana/OTel configuration
docs/       Architecture diagrams, runbooks, ADRs
tests/      Unit, integration, E2E, and load profiles
```
Refer to [`docs/manual-setup.md`](docs/manual-setup.md) for detailed manual provisioning instructions.

---

## Security & Privacy
- **Auth**: API keys or OIDC with RBAC roles (`admin`, `manager`, `user`).
- **Isolation**: sandboxed subprocesses/WASM with resource limits.
- **Supply chain**: signed modules (Cosign) with SBOM attestation.
- **Policies**: per-intent privacy levels (`local-only`, `allow-api`, `hybrid`), budget caps, latency targets.
- **Production tip**: enable mTLS for inter-service gRPC traffic.

---

## Roadmap
- IDE/MCP adapters for safe tool/file access.
- One-click spec wizard to bootstrap `.aionos/`.
- Connector pack (webhooks, messaging, IoT).

---

## License
Apache-2.0. See [`LICENSE`](LICENSE).

---

## 🇮🇷 معرفی فارسی
**AION-OS** یک سیستم‌عامل ماژولار برای ایجنت‌های هوش مصنوعی است که از هسته‌ی زمان‌بندی، مسیریاب مبتنی بر سیاست، و کنسول شیشه‌ای زنده تشکیل شده است.

### ویژگی‌ها
- معماری چندلایه: Gateway (TypeScript/Fastify)، Control (FastAPI)، Modules (Rust/WASM)، Console (Next.js).
- مسیریابی هوشمند: `local | api | hybrid` با سقف هزینه، SLA، و ریلود آنی.
- Spec-Driven: پوشه‌ی `.aionos/` برای استانداردسازی خروجی ایجنت‌ها از برنامه تا تست و مستند.
- دانش و ابزار امن: پایگاه دانش پروژه با ارجاع در UI و اتصال امن IDE/MCP.
- Real-time: استریم زنده‌ی لاگ، وضعیت تسک، حضور کاربران.
- امنیت: RBAC، کلید/SSO، Sandbox، امضای ماژول‌ها، SBOM.
- مشاهده‌پذیری: OTel، Prometheus، داشبوردهای Grafana.
- بیگ‌دیتا (اختیاری): Kafka→ClickHouse، Spark/Flink، Airflow، Superset.

### شروع سریع
1. شاخهٔ `AIONOS` را کلون و فایل‌های `.env` را تنظیم کنید.
2. `docker compose up -d` را اجرا کنید.
3. یک کلید ادمین بسازید و یک Task نمونه (REST/SSE) ارسال کنید.

### امنیت و حریم خصوصی
RBAC و OIDC، ایزوله‌سازی ماژول‌ها، امضای بسته‌ها، سیاست‌های حریم خصوصی بر اساس Intent. در محیط عملیاتی، **mTLS** را فعال کنید.

### مشاهده‌پذیری و بیگ‌دیتا
ردیابی و متریک‌ها با OTel/Prometheus؛ داشبوردهای آماده در Grafana. در حالت بیگ‌دیتا، جریان‌ها به ClickHouse متصل می‌شوند و وظایف تحلیلی با Spark/Flink و Airflow مدیریت می‌شوند.

### مجوز
Apache-2.0.
