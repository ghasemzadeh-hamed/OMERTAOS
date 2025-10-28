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
