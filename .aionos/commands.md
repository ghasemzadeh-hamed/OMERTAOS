# AION-OS — ChatOps / Agent Commands (EN/FA)

> These commands are prompts for your Agent/ChatOps terminal in Console (or CLI).  
> The agent must **read `.aionos/AGENT.md` and `/docs` first**.

## 1) English

### Planning & Scaffolding
- **/plan {intent} {inputs?}**
  - Read specs → produce task breakdown, acceptance tests, latency/cost budgets, rollback plan.
- **/scaffold {service} {feature}**
  - Generate minimal, runnable code (no placeholders), tests, docs; wire tracing & metrics.

### Implementation
- **/implement {service} {feature}**
  - Write code + tests; update OpenAPI/gRPC protos; ensure idempotency at gateway; commit with Conventional Commits.
- **/policy reload**
  - Call `POST /v1/router/policy/reload`; verify with health & smoke test.

### Verification
- **/test unit|e2e|load {service}**
  - Run tests; for load use `k6` profiles; export report links.
- **/observe**
  - Show OTEL trace sample (gateway→control→module), Prometheus metrics diffs, Grafana panels updated.

### Documentation & Delivery
- **/doc {area}**
  - Update README, ERD/sequence diagrams, API refs, runbook.
- **/deploy dev|staging|prod**
  - Compose/K8s apply with SBOM+sign; verify health, roll back on regression.

---

## 2) فارسی

### برنامه‌ریزی و اسکَفولد
- **/plan {intent} {inputs?}** → شکست تسک، تست پذیرش، بودجه تأخیر/هزینه، برنامه بازگشت.
- **/scaffold {service} {feature}** → کد اجرایی حداقلی + تست + مستندات + OTel.

### پیاده‌سازی
- **/implement {service} {feature}** → کدنویسی کامل با تست، پوشش قراردادها، Idempotency در Gateway.
- **/policy reload** → ریلود سیاست‌ها و بررسی سلامت.

### راستی‌آزمایی
- **/test unit|e2e|load {service}** → اجرای تست‌ها و گزارش.
- **/observe** → نمونه Trace و متریک‌ها و به‌روزرسانی داشبورد.

### مستندسازی و استقرار
- **/doc {area}** → به‌روزرسانی README/ERD/API/Runbook.
- **/deploy dev|staging|prod** → استقرار با SBOM/امضا و بررسی برگشت‌پذیری.
