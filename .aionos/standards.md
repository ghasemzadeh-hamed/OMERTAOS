# AION-OS — Engineering Standards (EN/FA)

## 1) English — Code, Infra, Security

### Language/Framework Conventions
- **TypeScript (Gateway/Console):**
  - ESLint + Prettier; strict TS; `zod` for schema validation at edges.
  - HTTP handlers: pure functions; side-effects isolated; idempotency keys via Redis.
- **Python (Control/FastAPI):**
  - `pydantic` models for all I/O; `httpx` for outbound; `asyncio` only.
  - Config via `pydantic-settings`; no globals; dependency injection for services.
- **Rust (Modules):**
  - `tokio` + `tonic`; `thiserror` for error taxonomy; `serde_json` I/O; timeouts & circuit breakers.
  - No network access unless allowed by policy; file I/O restricted to sandbox path.

### Architectural Standards
- **Contracts:** Task/Result schemas versioned (`schemaVersion`); backward-compatible additions only.
- **Policies:** editable YAML (intents/models/modules/privacy); hot-reload endpoint required.
- **Observability:** OTel spans must include `task_id`, `decision`, `engine.kind`, `latency_ms`.
- **Performance Budgets:** default P95 < 1200ms for “summarize”, < 2500ms for “rag-search”.

### Security Standards
- Secrets via env/secret store; never commit secrets.
- mTLS for inter-service gRPC in prod; TLS termination at gateway.
- **Cosign** signing for modules; **SBOM** generated on build; CI enforces verify step.
- Input validation at edges; allowlist tool-use; rate-limit per IP/key/intent.

### Git/CI Standards
- **Conventional Commits**; small PRs; linked issues; checked boxes:
  - [ ] Tests added/updated  [ ] Docs updated  [ ] Backward-compatible  [ ] Security reviewed
- CI pipeline: install → lint → unit → e2e → build → sbom → sign/verify.

---

## 2) فارسی — استانداردهای مهندسی

### کدنویسی
- **TS:** ESLint/Prettier، TS strict، اعتبارسنجی ورودی با Zod.
- **Python:** مدل‌های Pydantic، Async کامل، پیکربندی امن.
- **Rust:** gRPC با Tonic، خطاپذیری استاندارد، محدودیت‌های Sandbox.

### معماری
- قراردادهای نسخه‌دار، سیاست‌های قابل‌ریلود، مشاهده‌پذیری با شناسه‌های مشترک (task_id و…)،
- بودجه‌های کارایی (P95) برای اینتنت‌های پرکاربرد.

### امنیت
- مدیریت امن اسرار، mTLS، امضای ماژول‌ها، SBOM، Rate-Limit و Allowlist ابزارها.

### گیت/CI
- کامیت‌های قراردادی، PR کوچک، چک‌لیست کامل، پایپلاین استاندارد.
