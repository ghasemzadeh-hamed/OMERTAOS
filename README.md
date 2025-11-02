<p align="center">
  <a href="https://github.com/sponsors/ghasemzadeh-hamed" target="_blank" rel="noopener">
    <img src="https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-black?logo=githubsponsors" alt="Sponsor on GitHub">
  </a>
  &nbsp;
  <a href="https://tronscan.org/#/address/TFF6hgmr5h5fy8sEJS8sLYN81pm4rarkDM" target="_blank" rel="noopener">
    <img src="https://img.shields.io/badge/Donate-TRX%20(TRON)-red?logo=tron" alt="Donate TRX (TRON)">
  </a>
</p>

# AION‑OS (Agent Web‑OS)

AION‑OS is an opinionated operating system for AI agents. It combines a secure routing plane, a modular execution kernel, and a
Glass‑style web console so teams can orchestrate agents with predictable costs, auditable decisions, and real‑time feedback.

> 💡 Looking for فارسی؟ [به بخش فارسی بروید](#-معرفی-aion-os-fa).

---

## Table of contents

- [Why AION‑OS?](#why-aion-os)
- [Platform architecture](#platform-architecture)
- [Getting started](#getting-started)
  - [Linux quick install wizard](#linux-quick-install-wizard)
  - [Windows quick install wizard](#windows-quick-install-wizard)
  - [Docker Compose](#docker-compose)
  - [Headless / server usage](#headless--server-usage)
  - [Config‑as‑code bundles](#config-as-code-bundles)
  - [Terminal explorer (TUI)](#terminal-explorer-tui)
- [Local model runtimes](#local-model-runtimes)
- [Operations toolkit](#operations-toolkit)
  - [Webhooks](#webhooks)
  - [Knowledge & RAG demo](#knowledge--rag-demo)
  - [Edge install (Apache)](#edge-install-apache)
  - [Observability & big‑data overlay](#observability--big-data-overlay)
- [Developer workflow](#developer-workflow)
- [Security & privacy](#security--privacy)
- [Roadmap](#roadmap)
- [Donate](#donate)
- [License](#license)
- [معرفی فارسی](#-معرفی-aion-os-fa)

---

## Why AION‑OS?

- **Multi‑plane design:** Gateway (TypeScript/Fastify), Control (FastAPI), Execution Modules (Rust/WASM), and Console (Next.js)
  separate routing, policy, execution, and UX concerns.
- **Policy‑aware routing:** The router selects `local | api | hybrid` execution paths with per‑intent budgets, SLAs, and privacy
  guarantees that can be updated without redeploying services.
- **Spec‑driven delivery:** Repository‑level contracts under `.aionos/` keep planning, implementation, testing, and
  documentation aligned for each agent workflow.
- **Knowledge OS:** Project memory with citations, IDE/MCP integrations, and secure knowledge ingestion pipelines.
- **Realtime operations:** WebSocket/SSE streams expose agent activity, health, and audit trails in the console and CLI tools.
- **Defense in depth:** RBAC, API keys/OIDC, sandboxed modules, signed manifests, SBOM generation, and privacy policies per
  intent.

---

## Platform architecture

```text
Gateway/    Fastify router exposing REST/gRPC/SSE/WS with auth, quotas, idempotency
Control/    FastAPI orchestration, policy & budget management, storage adapters
Modules/    Rust/WASM execution units with signing and sandboxing
Console/    Next.js Glass UI (RTL ready) with NextAuth, task board, live logs
.aionos/    Spec contracts guiding planning (/plan) and delivery (/doc) outputs
Policies/   Intents, model routing, module manifests, privacy definitions
BigData/    Kafka → ClickHouse, Spark/Flink, Airflow, Superset overlays
Deploy/     Systemd/K8s, Prometheus/Grafana/OTel configs
Docs/       Runbooks, diagrams, ADRs
Tests/      Unit, integration, e2e, and load profiles
```

Refer to `docs/` for diagrams and runbooks, and to `deploy/` for production manifests.

---

## Getting started

### Prerequisites

- Docker and Docker Compose (v2+) on the host machine.
- Git for cloning the repository.
- Optional: NVIDIA container toolkit for GPU inference, TRON wallet for donations.

### Linux quick install wizard

Bootstrap a complete local or remote deployment with the Bash wizard. It prepares configuration, seeds defaults, and launches
Docker Compose with a local model provider preconfigured.

```bash
./install.sh
# Accepts AIONOS_CONFIG_PATH overrides and can be run over SSH on Linux hosts
```

- Works on Debian/Ubuntu/Fedora class systems with Docker available.
- Configures `.env`, seeds admin credentials, warms up a local LLM, and opens the onboarding UI when available.
- Ideal for local development or cloud VMs where you want the entire stack with a single command.

### Windows quick install wizard

Use the interactive PowerShell installer for Windows workstations or Windows Server. It guides you through ports, credentials,
and optional BigData overlays before launching Docker Compose.

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

- Prompts for repository/branch, admin credentials, service ports, and data backends.
- Supports local or remote Docker (with WSL2) and prints the resulting service URLs.
- Automatically writes `console/.env`, `gateway/.env`, and `control/.env` using your answers.

For a one‑shot bootstrap on Windows, you can also run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_all_win.ps1
```

### Docker Compose

```bash
# 1) Clone the repository
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

Once containers are healthy, the default endpoints are:

- Console → <http://localhost:3000>
- Gateway → <http://localhost:8080>
- Control API → <http://localhost:8001>
- Health endpoints → append `/healthz`

Default console credentials (for install scripts):

- username: `admin` (or email `admin@localhost`)
- password: `admin`

### Headless / server usage

```bash
# Create admin + seed provider without opening a browser
aion init --quickstart --no-browser \
  --admin-email admin@local --admin-pass 'Str0ngPass!' \
  --provider hybrid --api-key "$OPENAI_API_KEY"

# Health check
curl -sf http://127.0.0.1:8001/api/health
```

### Config‑as‑code bundles

Use atomic bundles for repeatable deployments and CI automation.

```bash
aion apply --bundle deploy/bundles/my-config.tgz --atomic --no-browser
aion doctor --verbose
```

Bundle layout:

```text
my-config/
  config/            providers.yaml · router.policy.yaml · data-sources.yaml
  modules/           */aip.yaml (+ cosign.pub)
  services/          aion-*.service
  env/               aion.env.example
  scripts/           pre-apply.sh · post-apply.sh · verify.sh
  VERSION            semantic version of this bundle
  CHECKSUMS.txt      sha256 sums for integrity
```

### Terminal explorer (TUI)

Launch an in-terminal explorer with a chat‑forward configuration bot and text‑friendly UI.

```bash
aion-explorer
# Opens a text-friendly explorer (w3m/lynx) or prints the local URL to open
# Tabs: Projects · Providers · Modules · DataSources · Router · Chat · Health · Logs · Admin
# Keys: ←/→ tabs · Ctrl+S Apply · Ctrl+E Export · Ctrl+J Jobs · q quit
```

---

## Local model runtimes

### Default (Ollama)

```bash
./install.sh
# Opens http://localhost:3000 (onboarding chat)
# Local LLM runs at http://127.0.0.1:11434
# Override via: AIONOS_LOCAL_MODEL="llama3.2:8b" ./install.sh
```

### GPU (vLLM)

Requirements: NVIDIA driver, NVIDIA Container Toolkit, optional `HF_TOKEN`.

```bash
docker compose -f docker-compose.yml -f docker-compose.vllm.yml up -d --build
# OpenAI compatible endpoint → http://localhost:8008/v1/chat/completions
```

### Switching engines

```yaml
# config/aionos.config.yaml
models:
  provider: local
  local:
    engine: vllm   # ollama | vllm
    model: Qwen/Qwen2.5-7B-Instruct
```

---

## Operations toolkit

### Webhooks

AION‑OS can normalize inbound webhooks into signed, idempotent JSON envelopes before queuing them for processing.

```http
POST /api/webhooks/{source}
Headers: X-Signature (HMACSHA256), X-Timestamp, Content-Type
Body:    raw (json | form | xml | binary)
```

Authorized webhooks must pass signature/auth checks, IP allowlists, content limits, and idempotency tokens.

Normalized envelope example:

```json
{
  "source": "github|stripe|odoo|custom-1",
  "event_type": "push|invoice.paid|...|unknown",
  "event_id": "evt_... or sha256(body)",
  "occurred_at": "ISO8601",
  "headers": {"user-agent": "...", "x-signature": "..."},
  "payload": {"...": "original fields"}
}
```

Events are queued to Redis/Kafka and routed by `source + event_type` to modules with retry/backoff and DLQ support. Idempotency is
enforced via Redis `SETNX` on `event_id` with TTL.

Quick test:

```bash
curl -s -X POST http(s)://<control-host>/api/webhooks/custom-1 \
  -H "Content-Type: application/json" \
  -H "X-Signature: $(echo -n '{"ping":1}' | openssl dgst -sha256 -hmac "$CUSTOM1_SECRET" -hex | sed 's/^.* //')" \
  -d '{"event_id":"evt_1","event":"ping","ping":1}'
```

### Knowledge & RAG demo

```bash
# Ingest Markdown/plain-text into Qdrant
curl -F "col=aionos-docs" -F "files=@README.md" http://localhost:8000/rag/ingest

# Query the collection
curl -X POST http://localhost:8000/rag/query \
  -H "content-type: application/json" \
  -d '{"collection":"aionos-docs","query":"What is AION-OS?","limit":3}'
```

### Edge install (Apache)

The interactive installer hardens the reverse proxy perimeter. It detects IPv4/IPv6, validates DNS, and configures Apache for
WebSocket/SSE aware reverse proxies.

```bash
make edge-setup
# Interactive prompts:
# 1) Domain Mode (SSL) or Local Mode
# 2) Subdomains or single-domain paths
# 3) Email for Let's Encrypt, IPv6 toggle
# Results: HTTPS vhosts + HSTS (Domain) OR local reverse proxies on 8088/8089/8090
```

- **Domain mode:** Issues Let's Encrypt certificates, enables `proxy`, `proxy_http`, `proxy_wstunnel`, `http2`, and injects
  security headers with SSE/WebSocket aware `ProxyPassMatch` rules.
- **Local mode:** Provisions non‑TLS proxies bound to `127.0.0.1` on ports `8088`, `8089`, and `8090` for Console, Gateway, and
  Control respectively.
- **IPv6:** Optional listener when AAAA records exist. The script surfaces mismatched DNS answers so you can update zone files
  before rerunning.

### Observability & big‑data overlay

- **Tracing & metrics:** OpenTelemetry instrumentation with Prometheus exporters and curated Grafana dashboards.
- **Pipeline overlay (optional):** Kafka → ClickHouse ingestion, Spark/Flink jobs, Airflow DAGs, and Superset BI dashboards.

---

## Developer workflow

- **Repository layout:**

  ```text
  Policies/   Intent routing, model configs, module manifests, privacy rules
  Deploy/     K8s manifests, Prometheus/Grafana/OTel configuration
  Docs/       Architecture diagrams, runbooks, ADRs
  Tests/      Unit, integration, E2E, and load profiles
  ```

- **Manual setup:** Refer to `docs/manual-setup.md` for step-by-step provisioning.
- **Testing matrix:**
  - Gateway → `npm test` (Vitest)
  - Control → `pytest`
  - Modules → `cargo test`
  - Console → Playwright E2E suite
  - Load → `k6` profiles

GitHub Actions (`.github/workflows/ci.yml`) keeps these tracks green and lint-checks the Linux wizard (`install.sh`), Windows wizard
(`install.ps1`), and the Apache edge installer so the quick-start flows remain CI verified across local, cloud, and perimeter modes.

---

## Security & privacy

- **Auth:** API keys or OIDC with RBAC roles (admin, manager, user).
- **Isolation:** Sandboxed subprocesses/WASM with resource limits.
- **Supply chain:** Signed modules (Cosign) with SBOM attestation.
- **Policies:** Per-intent privacy levels (`local-only`, `allow-api`, `hybrid`), budget caps, and latency targets.
- **Production tip:** Enable mutual TLS for inter-service gRPC traffic.

---

## Roadmap

- IDE/MCP adapters for safe tool/file access.
- One-click spec wizard to bootstrap `.aionos/`.
- Connector pack (webhooks, messaging, IoT).

---

## Donate

**TRON (TRX)**

- Address: `TFF6hgmr5h5fy8sEJS8sLYN81pm4rarkDM`
- Only send TRX / TRC20 assets to this address.

---

## License

Apache-2.0. See [`LICENSE`](LICENSE).

---

## 🇮🇷 معرفی AION-OS (FA)

AION‑OS یک سیستم‌عامل ماژولار برای ایجنت‌های هوش مصنوعی است که از هسته‌ی زمان‌بندی، مسیریاب مبتنی بر سیاست و کنسول شیشه‌ای زنده
تشکیل شده است.

**ویژگی‌ها**

- معماری چندلایه: Gateway (TypeScript/Fastify)، Control (FastAPI)، Modules (Rust/WASM)، Console (Next.js).
- مسیریابی هوشمند: `local | api | hybrid` با سقف هزینه، SLA و ریلود آنی.
- Spec-Driven: پوشه‌ی `.aionos/` برای استانداردسازی خروجی ایجنت‌ها از برنامه تا تست و مستندات.
- دانش و ابزار امن: پایگاه دانش پروژه با ارجاع در UI و اتصال امن IDE/MCP.
- Real-time: استریم زنده‌ی لاگ، وضعیت تسک، حضور کاربران.
- امنیت: RBAC، کلید/SSO، Sandbox، امضای ماژول‌ها، SBOM.
- مشاهده‌پذیری: OTel، Prometheus، داشبوردهای Grafana.
- بیگ‌دیتا (اختیاری): Kafka → ClickHouse، Spark/Flink، Airflow، Superset.

**شروع سریع**

1. شاخهٔ AIONOS را کلون و فایل‌های `.env` را تنظیم کنید.
2. `docker compose up -d` را اجرا کنید.
3. یک کلید ادمین بسازید و یک Task نمونه (REST/SSE) ارسال کنید.

**امنیت و حریم خصوصی**

RBAC و OIDC، ایزوله‌سازی ماژول‌ها، امضای بسته‌ها، سیاست‌های حریم خصوصی بر اساس Intent. در محیط عملیاتی، mTLS را فعال کنید.

**مشاهده‌پذیری و بیگ‌دیتا**

ردیابی و متریک‌ها با OTel/Prometheus؛ داشبوردهای آماده در Grafana. در حالت بیگ‌دیتا، جریان‌ها به ClickHouse متصل می‌شوند و
وظایف تحلیلی با Spark/Flink و Airflow مدیریت می‌شوند.

**مجوز**

Apache-2.0.
