
# AION-OS (Agent Web-OS) — Modular, Spec-Driven AI Agent OS

[FA ⭢ فارسی](#-معرفی-فارسی) · [EN ⭢ English](#-english-overview)

AION-OS is a **distributed, kernel-style operating system for AI agents**. It blends three proven ideas into one production platform:

1. **Spec-Driven Workflows** — project/user markdown specs (`.aionos/AGENT.md`, `policies/*.md`) steer agents to ship code to your standards (inspired by BuilderMethods Agent-OS). ([GitHub][1])
2. **Knowledge & Task OS for Coding** — RAG-backed knowledge, task graphs, and **MCP/IDE** integrations to supercharge coding agents (inspired by Archon). ([GitHub][2])
3. **Personal OS Modules** — assemble assistants, tutors, & device controllers with local-first privacy and plug-in connectors (inspired by OpenDAN). ([GitHub][3])

---

## ✨ Highlights

* **Multi-Plane Architecture:** Gateway (TS/Fastify), Control (FastAPI), Execution (Rust/WASM), Glass-UI Console (Next.js).
* **Spec-Driven Agents:** read `.aionos/AGENT.md` + repo docs to derive plans, acceptance criteria, and coding standards. ([GitHub][1])
* **Knowledge OS:** project KB + embeddings + citations; optional **MCP** to IDEs for tool/FS access (Archon-style). ([GitHub][4])
* **Personal Modules:** connectors for mail/Telegram/HTTP hooks/IoT; local execution path available (OpenDAN-style). ([GitHub][3])
* **Policy Router:** `local | api | hybrid` with budget/SLA.
* **Observability:** Prometheus/Grafana + OpenTelemetry; audit trail.
* **Big-Data Overlay (optional):** Kafka → ClickHouse; Spark/Flink; Airflow; Superset dashboards.

---

## 🚀 Quick Start (Docker Compose)

```bash
# 1) clone (AIONOS branch)
git clone -b AIONOS --single-branch https://github.com/ghasemzadeh-hamed/OMERTAOS.git
cd OMERTAOS

# 2) envs
cp .env.example .env
cp console/.env.example console/.env
cp control/.env.example control/.env

# 3) bring up core
docker compose up -d

# (optional) analytics stack
docker compose -f bigdata/docker-compose.bigdata.yml up -d
```

Open: **Console** [http://localhost:3000](http://localhost:3000) · **Gateway** [http://localhost:8080](http://localhost:8080) · health: `/healthz`.

Create an admin key (dev):

```env
AION_GATEWAY_API_KEYS=demo-key:admin|manager
```

Submit a task:

```bash
curl -X POST http://localhost:8080/v1/tasks \
  -H "X-API-Key: demo-key" -H "Content-Type: application/json" \
  -d '{"schemaVersion":"1.0","intent":"summarize","params":{"text":"Hello"}}'
```

Stream events (SSE):

```bash
curl -H "X-API-Key: demo-key" http://localhost:8080/v1/stream/<task_id>
```

---

## 🧱 Repository Layout

```
gateway/   # REST/gRPC/SSE/WS, auth, rate-limit, idempotency
control/   # FastAPI router + orchestrator + policy/budget SLA
modules/   # Rust tools (WASM/subprocess) + manifests (Cosign/SBOM)
console/   # Next.js Glass UI (fa/en + RTL), NextAuth, real-time
.aionos/   # <— spec-driven agent configs (AGENT.md, standards.md)
policies/  # intents.yml, models.yml, modules.yml, privacy.yml
bigdata/   # Kafka/Spark(or Flink)/ClickHouse/Airflow/Superset
deploy/    # Prometheus/Grafana, OTel; k6/load; CI/CD workflows
docs/      # ERD, sequences, API refs, runbooks
```

---

## 🧭 Spec-Driven Agenting (Agent-OS inspired)

Place a minimal spec in your repo so AION-OS agents **follow your standards on the first try**:

```
.aionos/
 ├─ AGENT.md            # Product spec, architecture guardrails, done-criteria
 ├─ standards.md        # Code style, review checklist, security rules
 └─ commands.md         # /plan /scaffold /implement /test /doc
```

**Workflow (suggested):**

1. `/plan` → break down tasks with acceptance tests;
2. `/scaffold` → create module skeletons;
3. `/implement` → open PRs;
4. `/test` → run unit/e2e;
5. `/doc` → update README/ERD.

These conventions mirror BuilderMethods Agent-OS’ philosophy (user-level + project-level specs) while mapped onto AION-OS planes. ([GitHub][1])

---

## 📚 Knowledge OS (Archon inspired)

* Project KB ingestion (`/docs`, ADRs, API refs) → embeddings + RAG;
* **MCP/IDE Hooks** for coding agents to read/write files & run tools safely;
* Task board with citations back to sources. (Archon positions itself as a knowledge & task OS for coding assistants). ([GitHub][2])

---

## 🧩 Personal OS Modules (OpenDAN inspired)

* Compose assistants (butler/tutor/ops) with local-first privacy;
* Connectors: Webhooks (HMAC), Telegram/Email, IoT device APIs;
* Teaming: multi-agent handoffs with shared memory. (OpenDAN emphasizes modular personal agents and interoperability.) ([GitHub][3])

---

## 🔐 Security

* RBAC + API keys/OIDC; sandboxed subprocess/WASM; signed modules (Cosign); SBOM.
* Privacy policies per intent: `local-only | allow-api | hybrid` with budget/latency caps.
* **Prod note:** enable mTLS for inter-service gRPC.

---

## 📊 Observability & Big-Data

* OpenTelemetry traces, Prometheus metrics; Grafana dashboards.
* Optional overlay: Kafka topics (`aion.tasks.*`, `aion.router.*`) ingested to ClickHouse; Spark/Flink jobs; Airflow DAGs; Superset BI.

---

## 🧪 Testing

* Unit: `npm test` (gateway), `pytest` (control), `cargo test` (modules)
* E2E: Playwright (console) + API smoke; Load: `k6` profiles.

---

## 🗺️ Roadmap (short)

* MCP adapters for VS Code/Cursor/Claude Code. ([GitHub][4])
* Spec wizards to bootstrap `.aionos/AGENT.md` from existing repos (Agent-OS style). ([GitHub][1])
* Personal connectors pack (OpenDAN-style modules & IoT). ([GitHub][3])

---

## 📝 License

Apache-2.0 (recommended).

---

## 🇮🇷 معرفی فارسی

**AION-OS** یک «سیستم‌عامل عامل‌ها» با سه ایدهٔ کلیدی است:

* **ورک‌فلوهای Spec-Driven** برای اینکه ایجنت‌ها دقیقاً مطابق استاندارد کدنویسی شما خروجی بدهند (ایده‌گرفته از Agent-OS). ([GitHub][1])
* **OS دانشی و تسکی برای کدنویسی** با RAG و اتصال MCP/IDE (الهام از Archon). ([GitHub][2])
* **ماژول‌های Personal OS** با اجرای محلی و کانکتور سرویس/IoT (الهام از OpenDAN). ([GitHub][3])

### شروع سریع

1. کلون `AIONOS`، تنظیم `.env`ها، اجرای `docker compose`.
2. ساخت کلید ادمین و ارسال Task نمونه (REST/SSE).
3. افزودن پوشه‌ی `.aionos/` و تعریف استانداردها تا ایجنت‌ها از روی آن کار کنند (Spec-Driven).

### امنیت، مشاهده‌پذیری و بیگ‌دیتا

RBAC، امضای ماژول‌ها، mTLS (محیط عملیاتی)، ردیابی OTel، متریک Prometheus، داشبورد Grafana. بیگ‌دیتا: Kafka→ClickHouse، Spark/Flink، Airflow، Superset.

---

### Acknowledgements

This README synthesizes ideas from: **BuilderMethods Agent-OS** (spec-driven agent workflows), **Archon** (knowledge+task OS for AI coding with MCP/IDE), and **OpenDAN** (personal modular AI OS). ([buildermethods.com][5])

---
