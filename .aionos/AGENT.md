# AION-OS — Project & Agent Spec (EN/FA)

## 1) English — Product & Technical Spec

### Objective
Build a modular, **kernel-style Agent OS** with four planes:
- **Gateway (TS/Fastify)** — REST/gRPC/WS/SSE, auth, rate-limit, idempotency, OTEL.
- **Control (FastAPI/Python)** — AI Decision Router (local|api|hybrid), Task Orchestrator, budgets/SLA, Postgres/Redis/Qdrant/Kafka.
- **Execution Modules (Rust/WASM/subprocess)** — sandboxed tools (embedding/transform/OCR/…); Cosign+SBOM.
- **Console (Next.js Glass UI)** — en/fa + RTL, NextAuth, RBAC, realtime task board.

### Non-Negotiable Constraints
- **Security first:** RBAC, API keys/OIDC, mTLS in prod, sandbox (seccomp/AppArmor), signed modules.
- **Observability:** OpenTelemetry traces + Prometheus metrics + Grafana dashboards.
- **Spec-Driven:** Agents MUST read this spec and `/docs` before planning.
- **No placeholders / No ellipses** in generated code.

### Key User Stories
- As an admin, I can define **policies** (`local-only | allow-api | hybrid`) per **intent** with budget & P95 latency.
- As a developer, I can register **modules** with signed manifests and see them in Console.
- As an operator, I can **reload router policy** without downtime: `POST /v1/router/policy/reload`.
- As a data engineer, I can enable **Big-Data overlay** (Kafka→ClickHouse, Spark/Flink, Airflow, Superset).

### Acceptance Criteria (AC)
- **AC1 — Compose Up:** `docker compose up` launches gateway, control, console, dbs; healthz passes.
- **AC2 — Router:** given Task JSON, router outputs `{decision, reason}` and dispatches correctly.
- **AC3 — Realtime:** task events stream over SSE/WS; Console shows live updates.
- **AC4 — Auth/RBAC:** NextAuth + roles (admin/manager/user) enforced on protected routes.
- **AC5 — Obs:** traces span gateway→control→module; Grafana shows runtime dashboards.
- **AC6 — Security:** signed module accepted; unsigned rejected with auditable reason.
- **AC7 — Big-Data (opt):** overlay boots; decisions & latency written to ClickHouse; Superset dashboards render.

### Definition of Ready (DoR)
- Intent, inputs, outputs, budgets (usd/tokens), SLA (latency_ms), privacy mode chosen.
- Test data & acceptance tests listed. Rollback plan noted.

### Definition of Done (DoD)
- Code + tests + docs updated; CI green (lint/unit/e2e/build); security checks pass; dashboards updated.

---

## 2) فارسی — مشخصات محصول و فنی

### هدف
پیاده‌سازی **سیستم‌عامل عامل‌ها** با چهار لایه: Gateway، Control، Modules، Console (UI شیشه‌ای).

### الزامات غیرقابل مذاکره
- امنیت (RBAC، OIDC/API Key، mTLS، Sandbox، امضای ماژول‌ها)،
- مشاهده‌پذیری (OTel/Prometheus/Grafana)،
- اجرای Spec-Driven (مطالعه این فایل و `/docs` قبل از برنامه‌ریزی)،
- بدون Placeholder و سه‌نقطه در کد نهایی.

### سناریوهای کاربری
- تعریف سیاست‌های اجرای **local/api/hybrid** با بودجه و SLA،
- رجیستر ماژول‌های امضاشده و مشاهده در کنسول،
- ریلود سیاست‌ها بدون قطعی،
- فعال‌سازی لایه بیگ‌دیتا و مشاهده داشبوردها.

### معیارهای پذیرش (AC)
مطابق بخش انگلیسی (AC1…AC7).

### DoR / DoD
مطابق بخش انگلیسی.
