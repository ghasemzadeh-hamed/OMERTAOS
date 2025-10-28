# AION-OS (Agent Web-OS) — Next-Gen Modular AI Agent OS
[FA ⭢ فارسی](#-معرفی-فارسی) · [EN ⭢ English](#-english-overview)

Build, route, and scale AI agents like a pro.  
AION-OS is a **kernel-style, distributed OS for AI agents** with a sleek **Glass-UI** console, **policy-aware router**, and **local-first privacy**. Ship fast. Run anywhere.

---

## ⚡ What You Get
- **Multi-Plane Architecture** → Gateway (TS/Fastify), Control (FastAPI), Execution (Rust/WASM), Console (Next.js).
- **Policy Router** → `local | api | hybrid` with budgets & SLAs (+ live reload).
- **Spec-Driven Agents** → repo-level standards in `.aionos/` guide agents from plan → PR → test → docs.
- **Knowledge OS** → project knowledge base with citations surfaced in UI; safe tools via IDE/MCP hooks.
- **Realtime Everything** → WS/SSE streams, presence, live logs, health.
- **Security by Default** → RBAC, API keys/OIDC, sandboxed modules, signed manifests, SBOM.
- **Observability** → OpenTelemetry, Prometheus, Grafana dashboards.
- **Big-Data Mode (optional)** → Kafka → ClickHouse, Spark/Flink, Airflow, Superset.

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1) Clone the AIONOS branch
git clone -b AIONOS --single-branch https://github.com/ghasemzadeh-hamed/OMERTAOS.git
cd OMERTAOS

# 2) Env setup
cp .env.example .env
cp console/.env.example console/.env
cp control/.env.example control/.env

# 3) Bring up core services
docker compose up -d

# (optional) Analytics stack
docker compose -f bigdata/docker-compose.bigdata.yml up -d
````

### Quick-Start with Local LLM
#### Default (CPU/GPU auto) — Ollama
```bash
./install.sh
# opens http://localhost:3000 (Onboarding chat)
# Local LLM at http://127.0.0.1:11434
# Override defaults via env vars, e.g. AIONOS_LOCAL_MODEL="llama3.2:8b" ./install.sh
```

#### With GPU — vLLM (optional)
Requirements: NVIDIA driver + NVIDIA Container Toolkit + (optional) `HF_TOKEN`
```bash
docker compose -f docker-compose.yml -f docker-compose.vllm.yml up -d --build
# vLLM OpenAI endpoint -> http://localhost:8008/v1/chat/completions
```

#### Switch engine
Edit `config/aionos.config.yaml`:
```yaml
models:
  provider: local
  local:
    engine: vllm   # ollama | vllm
    model: Qwen/Qwen2.5-7B-Instruct
```

### Agent Mode (demo)
- Page: `/agent` on Console
- Env: `NEXT_PUBLIC_CONTROL_BASE`, `NEXT_PUBLIC_AGENT_API_TOKEN`
- Optional envs: `AIONOS_LOCAL_MODEL`, `OLLAMA_HOST`, `VLLM_HOST`

Security tips:
- Protect `/agent/*` & `/admin/onboarding/*` behind private network or auth.
- Do not commit secrets; use Docker/Swarm/K8s secrets or SOPS/Vault.

### Onboarding Chat (pet-bot)
- Visit `http://localhost:3000/onboarding` on first launch to seed admin, model provider, and gateway settings via the Persian chat wizard.
- Backend endpoints live under `/admin/onboarding/*` on the control plane.

### RAG Demo
- Ingest Markdown or plaintext into Qdrant:

```bash
curl -F "col=aionos-docs" -F "files=@README.md" http://localhost:8000/rag/ingest
```

- Query the collection:

```bash
curl -X POST http://localhost:8000/rag/query \
  -H "content-type: application/json" \
  -d '{"collection":"aionos-docs","query":"What is AION-OS?","limit":3}'
```

### Smoke E2E script
- Run `./scripts/smoke_e2e.sh` after the stack is up to ping health, agent, and RAG endpoints.

Open **Console** → `http://localhost:3000`
Open **Gateway** → `http://localhost:8080`
Health endpoints → `/healthz`

**Dev admin key (example):**

```env
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

**Fire a task (REST):**

```bash
curl -X POST http://localhost:8080/v1/tasks \
  -H "X-API-Key: demo-key" -H "Content-Type: application/json" \
  -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"Hello AION-OS!"}}'
```

**Follow live events (SSE):**

```bash
curl -H "X-API-Key: demo-key" http://localhost:8080/v1/stream/<task_id>
```

---

## 🧱 Repository Layout

```
gateway/    # REST/gRPC/SSE/WS, auth, rate-limit, idempotency
control/    # FastAPI router + orchestrator + policy/budget SLA + storage
modules/    # Rust tools (WASM/subprocess) + manifests + signing
console/    # Next.js Glass UI (fa/en + RTL), NextAuth, realtime task board
.aionos/    # <— spec-driven agent configs (AGENT.md, standards.md, commands.md)
policies/   # intents.yml, models.yml, modules.yml, privacy.yml (hot-reloadable)
bigdata/    # Kafka, Spark/Flink, ClickHouse, Airflow, Superset (optional)
deploy/     # Prometheus, Grafana, OTel configs
docs/       # ERD, sequences, API refs, runbooks
tests/      # unit, e2e, load profiles
```

---

## 🧭 Spec-Driven Agenting

Standardize outcomes with repo-native specs:

```
.aionos/
 ├─ AGENT.md        # product spec, guardrails, acceptance
 ├─ standards.md    # code style, security, review checklist
 └─ commands.md     # /plan /scaffold /implement /test /doc
```

**Flow:** `/plan` → `/scaffold` → `/implement` → `/test` → `/doc`
Agents read these specs, follow policies, and open PRs with tests + docs.

---

## 🔐 Security & Privacy

* **Auth**: API keys/OIDC, RBAC (admin/manager/user)
* **Isolation**: sandboxed subprocess/WASM, resource limits
* **Supply Chain**: signed modules (Cosign), SBOM
* **Policies**: privacy per intent (`local-only | allow-api | hybrid`), budget caps, latency targets
* **Prod Tip**: enable mTLS for inter-service gRPC

---

## 📊 Observability & Big-Data

* **Tracing/Metrics**: OTel + Prometheus; curated Grafana dashboards
* **Pipelines (optional)**: Kafka topics → ClickHouse; Spark/Flink jobs; Airflow DAGs; Superset BI

---

## 🧪 Testing

* Gateway → `npm test` (Vitest)
* Control → `pytest`
* Modules → `cargo test`
* Console → Playwright e2e
* Load → `k6` profiles

---

## 🗺️ Roadmap

* IDE/MCP adapters for safe tool/file access
* One-click spec wizard to bootstrap `.aionos/`
* Connector pack (webhooks, messaging, IoT)

---

## 📝 License

**Apache-2.0** (recommended). See `LICENSE`.

---

## 🇮🇷 معرفی فارسی

**AION-OS** یک سیستم‌عامل ماژولار برای ایجنت‌های هوش مصنوعی است: هسته‌ی زمان‌بندی و حافظه‌ی اشتراکی، مسیریاب مبتنی‌بر سیاست، و کنسول وب شیشه‌ای برای مشاهده و کنترل زنده.

### ویژگی‌ها

* **معماری چندلایه**: Gateway (TypeScript/Fastify)، Control (FastAPI)، Modules (Rust/WASM)، Console (Next.js)
* **مسیریابی هوشمند**: `local | api | hybrid` با سقف هزینه و SLA و ریلود در لحظه
* **Spec-Driven**: پوشه‌ی `.aionos/` برای استانداردسازی خروجی ایجنت‌ها (از برنامه تا تست و مستند)
* **دانش و ابزار امن**: پایگاه دانشی پروژه با ارجاع در UI و اتصال امن IDE/MCP
* **Real-time**: استریم زندهٔ لاگ، وضعیت تسک، حضور کاربران
* **امنیت**: RBAC، کلید/SSO، Sandbox، امضای ماژول‌ها، SBOM
* **مشاهده‌پذیری**: OTel، Prometheus، داشبوردهای Grafana
* **بیگ‌دیتا (اختیاری)**: Kafka→ClickHouse، Spark/Flink، Airflow، Superset

### شروع سریع

1. کلون شاخهٔ `AIONOS` و تنظیم `.env`ها
2. اجرای `docker compose up -d`
3. ساخت کلید ادمین و ارسال یک Task نمونه (REST/SSE)

### امنیت و حریم خصوصی

RBAC و OIDC، ایزوله‌سازی ماژول‌ها، امضای بسته‌ها، سیاست‌های حریم خصوصی بر اساس Intent. در محیط عملیاتی، **mTLS** را فعال کنید.

### مشاهده‌پذیری و بیگ‌دیتا

ردیابی و متریک‌ها با OTel/Prometheus؛ داشبوردهای آماده در Grafana. در حالت بیگ‌دیتا، جریان‌ها به ClickHouse وصل می‌شوند و وظایف تحلیلی با Spark/Flink و Airflow مدیریت می‌شوند.

### مجوز

Apache-2.0.


```
