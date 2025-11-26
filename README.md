# 🧠 oMerTaOS AION

AION is a hybrid operating system for autonomous AI agents that links low-level kernels, a policy-aware control plane, and a web console into one cohesive platform. It runs on bare metal, VMs, WSL, and containers so teams can orchestrate agents and ML workloads across edge, cloud, and enterprise environments.

---

## Platform overview

- **Kernel + registry** — Rust kernels in [`kernel/`](kernel) and [`kernel-multitenant/`](kernel-multitenant) schedule tenant-aware agent tasks. Registry manifests keep model and policy execution reproducible.
- **Control services** — Python workers under [`aion/`](aion) manage agent memory, task routing, and policy execution, backed by database and queue integrations configured in [`aion/config`](aion/config).
- **Gateway** — The TypeScript gateway in [`gateway/`](gateway) proxies API, auth, and model traffic between clients, the control plane, and runtime backends.
- **Console (Glass)** — The Next.js dashboard in [`console/`](console) provides setup, monitoring, and policy automation with authenticated flows and live task streams (SSE/WebSockets).
- **AI registry & models** — Registry metadata in [`ai_registry/REGISTRY.yaml`](ai_registry/REGISTRY.yaml) and model definitions in [`models/`](models) keep agent toolchains versioned and auditable.
- **Policies & agents** — Reference agents, policy bundles, and catalogs live under [`agents/`](agents), [`policies/`](policies), and [`config/agent_catalog`](config/agent_catalog), aligning runtime schemas with the console deployment wizards.

## Architecture at a glance

- **Installer & profiles** — [`core/`](core) and [`config/`](config) render `.env` files, systemd/NSSM units, and profile defaults. Profiles (`user`, `professional`, `enterprise-vip`) toggle ML tooling, Kubernetes hooks, LDAP, and hardening. [`configs/`](configs) and the compose overlays keep containerized deployments consistent.
- **Control plane classes & relationships** — The `aion` package organizes agents, memory, tasks, and workers into cohesive modules. Control APIs exposed through the gateway manage agent lifecycle (`/api/agents`), deployments (`/api/agents/{id}/deploy`), and catalog discovery (`/api/agent-catalog`). Catalog recipes and form schemas in [`config/agent_catalog/recipes`](config/agent_catalog/recipes) map directly to console wizards and validation logic.
- **Console dashboards** — The Glass console ships authenticated dashboards for agent catalogs, "My Agents", policy editors, task boards, telemetry, and LatentBox tool discovery. NextAuth handles local credentials and Google OAuth; TanStack Query drives optimistic updates; SSE/WebSockets stream live task/status changes.
- **AI registry & model plumbing** — Registry entries referenced as `model://` are resolved through the gateway to runtime backends. Model manifests in [`models/`](models) mirror registry metadata for deterministic builds and audits.
- **Security & compliance** — Hardening levels (`none`, `standard`, `cis-lite`) apply UFW, Fail2Ban, and Auditd. Secure Boot, full-disk encryption, and update cadence are documented under [`docs/security`](docs/security). First-boot automation patches hosts and captures logs at `/var/log/aionos-firstboot.log`.

## Quick start

### Linux (Docker Engine)

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./install.sh --profile user            # or professional / enterprise-vip
```

- The wrapper delegates to [`scripts/quicksetup.sh`](scripts/quicksetup.sh), which ensures prerequisites, renders `.env` from [`config/templates/.env.example`](config/templates/.env.example), and starts Docker Compose (default `docker-compose.yml`; pass `--local` for [`docker-compose.local.yml`](docker-compose.local.yml)).
- Add `--update` to pull the latest commits before launching services.

### Windows 11 / WSL2

```powershell
git clone https://github.com/Hamedghz/OMERTAOS.git
Set-Location OMERTAOS
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
pwsh ./install.ps1 -Profile user       # or professional / enterprise-vip
```

- Runs from Windows or WSL terminals; Docker Desktop must be enabled with WSL integration.
- Pass `-Local` for the developer overlay or `-Update` to fetch new commits before compose is invoked.

### Fast path (Docker Compose quickstart)

- Copy [`dev.env`](dev.env) to `.env` (or let `quick-install.sh` / `quick-install.ps1` do it automatically).
- Generate dev certs/JWT keys and start the stack:

```bash
./quick-install.sh
```

```powershell
./quick-install.ps1
```

This path uses [`docker-compose.quickstart.yml`](docker-compose.quickstart.yml) with dev certificates and JWT keys under `config/certs/dev` and `config/keys`.

### Other flows

Detailed guides for ISO, native Linux, WSL, and Docker modes live in [`docs/quickstart.md`](docs/quickstart.md). ISO and native installers gate destructive actions behind the `AIONOS_ALLOW_INSTALL` flag.

### QuickStart (Windows + Docker Desktop)

- Prerequisites: Docker Desktop with WSL2 backend enabled, Git, and PowerShell 7+.
- Steps:
  1. `git clone https://github.com/Hamedghz/OMERTAOS.git`
  2. `cd OMERTAOS`
  3. `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\quicksetup.ps1`
  4. `docker compose up -d`
  5. Open the services:
     - Console UI: http://localhost:3000
     - Gateway health: http://localhost:8080/healthz

The default profile is `user`, which keeps the stack lightweight while enabling the console, gateway, and control plane.

## Repository map

| Path | Purpose |
| ---- | ------- |
| [`aion/`](aion) | Python services and workers coordinating agent memory, policy execution, and task orchestration. |
| [`console/`](console) | Next.js + React Glass console with setup wizard, authenticated dashboards, and multilingual support. |
| [`gateway/`](gateway) | TypeScript gateway proxying API/auth/model traffic to control services and runtime backends. |
| [`core/`](core) | Installer assets, first-boot automation, kiosk tooling, and OS packaging logic. |
| [`kernel/`](kernel) / [`kernel-multitenant/`](kernel-multitenant) | Rust kernels and registry definitions for single- and multi-tenant scheduling. |
| [`scripts/`](scripts) | Automation utilities for quick setup, smoke tests, installers, and CI helpers. |
| [`config/`](config) / [`configs/`](configs) | Environment templates, systemd/NSSM units, reverse-proxy manifests, and profile wiring. |
| [`agents/`](agents) / [`policies/`](policies) | Reference agent definitions and policy bundles exercised by the runtime and console. |
| [`models/`](models) | Model manifests aligned with the AI registry for reproducible deployments. |
| [`ai_registry/`](ai_registry) | Central registry metadata consumed by gateways, agents, and policies. |

## Profiles

| Profile          | Default scope             | ML tooling      | Platform add-ons               | Hardening |
| ---------------- | ------------------------- | --------------- | ------------------------------ | --------- |
| user             | Gateway, control, console | Disabled        | Docker (lightweight)           | none      |
| professional (pro)| Gateway, control, console | Jupyter, MLflow | Docker                         | standard  |
| enterprise-vip   | Gateway, control, console | Jupyter, MLflow | Docker, Kubernetes hooks, LDAP | cis-lite  |

Profile manifests reside in [`config/profiles`](config/profiles) with defaults in [`core/installer/profile/defaults`](core/installer/profile/defaults). The installer pipeline renders `.env` files from [`config/templates/.env.example`](config/templates/.env.example) before first-boot automation enables services.

## Docker Compose overlays

[`docker-compose.yml`](docker-compose.yml) is the production baseline. Overlays extend it for focused scenarios:

- [`docker-compose.local.yml`](docker-compose.local.yml) – developer profile with lightweight defaults.
- [`docker-compose.obsv.yml`](docker-compose.obsv.yml) – adds observability tooling (OTel collector, dashboards).
- [`docker-compose.vllm.yml`](docker-compose.vllm.yml) – GPU-enabled vLLM runtime for large model experiments.

Combine overlays with `docker compose -f docker-compose.yml -f <overlay> up -d` to keep configurations in sync.

## Agent catalog and runtime wiring

- Agent templates live in [`config/agent_catalog/agents.yaml`](config/agent_catalog/agents.yaml) with per-template recipes in [`config/agent_catalog/recipes`](config/agent_catalog/recipes).
- Control APIs exposed via the gateway manage catalog discovery and agent lifecycle:
  - `GET /api/agent-catalog`, `GET /api/agent-catalog/{id}`
  - `GET /api/agents`, `POST /api/agents`, `PATCH /api/agents/{id}`, `POST /api/agents/{id}/deploy`, `POST /api/agents/{id}/disable`
- Console pages `/agents/catalog` and `/agents/my-agents` render dynamic forms from the same schemas and let users deploy agents with correct tenancy headers.
- LatentBox discovery (feature-flagged via `FEATURE_LATENTBOX_RECOMMENDATIONS`) hydrates an external tool registry from [`config/latentbox/tools.yaml`](config/latentbox/tools.yaml) and exposes sync/search endpoints alongside console UIs.

## Security, updates, and compliance

- First boot runs `apt-get update && apt-get upgrade` and `snap refresh`, then installs profile-specific services; logs persist at `/var/log/aionos-firstboot.log`.
- Secure Boot, full-disk encryption, and CIS-lite hardening are documented in [`docs/security`](docs/security), along with update cadence and CVE tracking.
- Installer flows gate destructive actions behind `AIONOS_ALLOW_INSTALL` and publish SBOM/signing steps described in [`docs/release.md`](docs/release.md).

## Hardware compatibility

Compatibility matrices (GPU, NIC, Wi‑Fi, firmware) and the reporting process live in [`docs/hcl`](docs/hcl). Detection scripts under `core/installer/bridge/tasks` keep hardware checks automated.

## Documentation hub

Enterprise-facing runbooks start at [`docs/README.md`](docs/README.md): quickstart guides, install modes, profiles, security baselines, troubleshooting, release, privacy, and hardware compatibility.

## Contributing and license

Please review [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), and [SECURITY.md](SECURITY.md) before submitting changes. AION-OS is distributed under the [Apache 2.0 license](LICENSE).

---

## نسخه فارسی

# 🧠 اومرتا او‌اِس آیون

آیون یک سیستم‌عامل ترکیبی برای عامل‌های هوش مصنوعی خودمختار است که هسته‌های سطح پایین، صفحه کنترل آگاه از سیاست و کنسول وب را در یک پلتفرم منسجم پیوند می‌دهد. این سیستم روی سخت‌افزار فیزیکی، ماشین مجازی، WSL و کانتینر اجرا می‌شود تا تیم‌ها بتوانند عامل‌ها و بارهای کاری یادگیری ماشین را در لبه، ابر و محیط‌های سازمانی سامان‌دهی کنند.

---

## نمای کلی پلتفرم

- **هسته و رجیستری** — هسته‌های نوشته‌شده با Rust در [`kernel/`](kernel) و [`kernel-multitenant/`](kernel-multitenant) وظایف عامل را با آگاهی از مستأجر زمان‌بندی می‌کنند. مانیفست‌های رجیستری اجرای مدل و سیاست را قابل تکرار نگه می‌دارند.
- **سرویس‌های کنترل** — کارگران پایتونی در [`aion/`](aion) حافظه عامل، مسیریابی وظایف و اجرای سیاست را مدیریت می‌کنند و به پایگاه‌داده و صف‌هایی متکی هستند که در [`aion/config`](aion/config) پیکربندی می‌شوند.
- **دروازه** — دروازه TypeScript در [`gateway/`](gateway) ترافیک API، احراز هویت و مدل را بین کلاینت‌ها، صفحه کنترل و پشتیبان‌های اجرایی پروکسی می‌کند.
- **کنسول (Glass)** — داشبورد Next.js در [`console/`](console) راه‌اندازی، نظارت و خودکارسازی سیاست را با جریان‌های زنده وظایف (SSE/WebSockets) و احراز هویت‌شده ارائه می‌دهد.
- **رجیستری هوش مصنوعی و مدل‌ها** — فراداده رجیستری در [`ai_registry/REGISTRY.yaml`](ai_registry/REGISTRY.yaml) و تعریف‌های مدل در [`models/`](models) زنجیره ابزار عامل را نسخه‌مند و قابل ممیزی نگه می‌دارند.
- **سیاست‌ها و عامل‌ها** — عامل‌های مرجع، بسته‌های سیاست و کاتالوگ‌ها در [`agents/`](agents)، [`policies/`](policies) و [`config/agent_catalog`](config/agent_catalog) قرار دارند و طرحواره‌های زمان اجرا را با ویزاردهای استقرار کنسول هماهنگ می‌کنند.

## معماری در یک نگاه

- **نصاب و پروفایل‌ها** — [`core/`](core) و [`config/`](config) فایل‌های `.env`، واحدهای systemd/NSSM و پیش‌فرض‌های پروفایل را تولید می‌کنند. پروفایل‌ها (`user`، `professional`، `enterprise-vip`) ابزارهای ML، هوک‌های Kubernetes، LDAP و سخت‌سازی را فعال یا غیرفعال می‌کنند. [`configs/`](configs) و لایه‌های compose برای استقرارهای کانتینری همگام می‌مانند.
- **کلاس‌ها و روابط صفحه کنترل** — بسته `aion` عامل‌ها، حافظه، وظایف و کارگران را در ماژول‌های یکپارچه سازمان‌دهی می‌کند. APIهای کنترل که از طریق دروازه منتشر می‌شوند چرخه عمر عامل (`/api/agents`)، استقرار (`/api/agents/{id}/deploy`) و کشف کاتالوگ (`/api/agent-catalog`) را مدیریت می‌کنند. دستورالعمل‌های کاتالوگ و طرحواره‌های فرم در [`config/agent_catalog/recipes`](config/agent_catalog/recipes) مستقیماً به ویزاردهای کنسول و منطق اعتبارسنجی نگاشت می‌شوند.
- **داشبوردهای کنسول** — کنسول Glass داشبوردهای احراز هویت‌شده برای کاتالوگ عامل، «عامل‌های من»، ویرایشگرهای سیاست، تابلوهای وظیفه، تلماتری و کشف ابزار LatentBox ارائه می‌دهد. NextAuth اعتبارهای محلی و Google OAuth را مدیریت می‌کند؛ TanStack Query به‌روزرسانی‌های خوش‌بینانه را پیش می‌برد؛ SSE/WebSockets تغییرات زنده وظیفه/وضعیت را پخش می‌کنند.
- **رجیستری هوش مصنوعی و مسیردهی مدل** — ورودی‌های رجیستری با پیشوند `model://` از طریق دروازه به پشتیبان‌های زمان اجرا حل می‌شوند. مانیفست‌های مدل در [`models/`](models) برای ساخت‌های قطعی و ممیزی با فراداده رجیستری همسو هستند.
- **امنیت و انطباق** — سطوح سخت‌سازی (`none`، `standard`، `cis-lite`) UFW، Fail2Ban و Auditd را اعمال می‌کنند. Secure Boot، رمزگذاری کامل دیسک و برنامه به‌روزرسانی در [`docs/security`](docs/security) مستند شده‌اند. خودکارسازی اولین بوت میزبان را به‌روزرسانی کرده و لاگ‌ها را در `/var/log/aionos-firstboot.log` ثبت می‌کند.

## شروع سریع

### لینوکس (Docker Engine)

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./install.sh --profile user            # یا professional / enterprise-vip
```

- این بسته به [`scripts/quicksetup.sh`](scripts/quicksetup.sh) واگذار می‌شود که پیش‌نیازها را بررسی می‌کند، `.env` را از [`config/templates/.env.example`](config/templates/.env.example) می‌سازد و Docker Compose را آغاز می‌کند (پیش‌فرض `docker-compose.yml`؛ برای [`docker-compose.local.yml`](docker-compose.local.yml) از `--local` استفاده کنید).
- برای کشیدن آخرین کامیت‌ها پیش از راه‌اندازی سرویس‌ها، `--update` را اضافه کنید.

### ویندوز 11 / WSL2

```powershell
git clone https://github.com/Hamedghz/OMERTAOS.git
Set-Location OMERTAOS
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
pwsh ./install.ps1 -Profile user       # یا professional / enterprise-vip
```

- قابل اجرا از ترمینال ویندوز یا WSL است؛ Docker Desktop باید با یکپارچه‌سازی WSL فعال باشد.
- از `-Local` برای لایه توسعه‌دهنده یا از `-Update` برای گرفتن کامیت‌های تازه پیش از اجرای compose استفاده کنید.

### مسیر سریع (Docker Compose quickstart)

- [`dev.env`](dev.env) را به `.env` کپی کنید (یا اجازه دهید `quick-install.sh` / `quick-install.ps1` این کار را انجام دهند).
- گواهی‌های توسعه و کلیدهای JWT را بسازید و استک را آغاز کنید:

```bash
./quick-install.sh
```

```powershell
./quick-install.ps1
```

این مسیر از [`docker-compose.quickstart.yml`](docker-compose.quickstart.yml) با گواهی‌های توسعه و کلیدهای JWT در `config/certs/dev` و `config/keys` استفاده می‌کند.

### مسیرهای دیگر

راهنماهای جزئی برای حالت‌های ISO، لینوکس بومی، WSL و Docker در [`docs/quickstart.md`](docs/quickstart.md) موجود است. نصاب ISO و بومی اقدامات مخرب را پشت متغیر `AIONOS_ALLOW_INSTALL` محافظت می‌کنند.

## نقشه مخزن

| مسیر | کاربرد |
| ---- | ------- |
| [`aion/`](aion) | سرویس‌ها و کارگران پایتونی که حافظه عامل، اجرای سیاست و ارکستراسیون وظایف را هماهنگ می‌کنند. |
| [`console/`](console) | کنسول React + Next.js با ویزارد راه‌اندازی، داشبوردهای احراز هویت‌شده و پشتیبانی چندزبانه. |
| [`gateway/`](gateway) | دروازه TypeScript که ترافیک API/احراز هویت/مدل را به سرویس‌های کنترل و پشتیبان‌های زمان اجرا پروکسی می‌کند. |
| [`core/`](core) | دارایی‌های نصاب، خودکارسازی اولین بوت، ابزارهای کیوسک و منطق بسته‌بندی سیستم‌عامل. |
| [`kernel/`](kernel) / [`kernel-multitenant/`](kernel-multitenant) | هسته‌های Rust و تعاریف رجیستری برای زمان‌بندی تک‌مستأجر و چندمستأجر. |
| [`scripts/`](scripts) | ابزارهای خودکارسازی برای راه‌اندازی سریع، تست دود، نصاب‌ها و کمک‌های CI. |
| [`config/`](config) / [`configs/`](configs) | الگوهای محیطی، واحدهای systemd/NSSM، مانیفست‌های پروکسی معکوس و سیم‌کشی پروفایل. |
| [`agents/`](agents) / [`policies/`](policies) | تعریف‌های عامل و بسته‌های سیاست مرجع که توسط زمان اجرا و کنسول استفاده می‌شوند. |
| [`models/`](models) | مانیفست‌های مدل هماهنگ با رجیستری هوش مصنوعی برای استقرارهای قابل تکرار. |
| [`ai_registry/`](ai_registry) | فراداده رجیستری مرکزی که توسط دروازه‌ها، عامل‌ها و سیاست‌ها مصرف می‌شود. |

## پروفایل‌ها

| پروفایل            | دامنه پیش‌فرض             | ابزار ML         | افزودنی‌های پلتفرم             | سخت‌سازی |
| ------------------ | ------------------------- | ---------------- | ------------------------------ | --------- |
| user               | Gateway، control، console | غیرفعال          | Docker (سبک)                   | none      |
| professional (pro) | Gateway، control، console | Jupyter، MLflow  | Docker                         | standard  |
| enterprise-vip     | Gateway، control، console | Jupyter، MLflow  | Docker، هوک‌های Kubernetes، LDAP | cis-lite |

مانیفست‌های پروفایل در [`config/profiles`](config/profiles) قرار دارند و پیش‌فرض‌ها در [`core/installer/profile/defaults`](core/installer/profile/defaults) تعریف شده‌اند. خط لوله نصاب، پیش از فعال‌سازی سرویس‌ها در اولین بوت، فایل‌های `.env` را از [`config/templates/.env.example`](config/templates/.env.example) می‌سازد.

## لایه‌های Docker Compose

[`docker-compose.yml`](docker-compose.yml) خط پایه تولید است. لایه‌ها برای سناریوهای متمرکز آن را گسترش می‌دهند:

- [`docker-compose.local.yml`](docker-compose.local.yml) – پروفایل توسعه‌دهنده با پیش‌فرض‌های سبک.
- [`docker-compose.obsv.yml`](docker-compose.obsv.yml) – ابزارهای مشاهده‌پذیری (کلکتور OTel، داشبوردها) را اضافه می‌کند.
- [`docker-compose.vllm.yml`](docker-compose.vllm.yml) – زمان اجرای vLLM با GPU برای آزمایش مدل‌های بزرگ را فعال می‌کند.

لایه‌ها را با `docker compose -f docker-compose.yml -f <overlay> up -d` ترکیب کنید تا پیکربندی‌ها همگام بمانند.

## کاتالوگ عامل و سیم‌کشی زمان اجرا

- الگوهای عامل در [`config/agent_catalog/agents.yaml`](config/agent_catalog/agents.yaml) قرار دارند و دستورالعمل‌های هر الگو در [`config/agent_catalog/recipes`](config/agent_catalog/recipes) تعریف شده‌اند.
- APIهای کنترل که از طریق دروازه در دسترس هستند کشف کاتالوگ و چرخه عمر عامل را مدیریت می‌کنند:
  - `GET /api/agent-catalog`, `GET /api/agent-catalog/{id}`
  - `GET /api/agents`, `POST /api/agents`, `PATCH /api/agents/{id}`, `POST /api/agents/{id}/deploy`, `POST /api/agents/{id}/disable`
- صفحات کنسول `/agents/catalog` و `/agents/my-agents` فرم‌های پویا را از همین طرحواره‌ها می‌سازند و به کاربران اجازه می‌دهند عامل‌ها را با سربرگ‌های درست مستأجر مستقر کنند.
- کشف LatentBox (از طریق ویژگی `FEATURE_LATENTBOX_RECOMMENDATIONS`) یک رجیستری ابزار خارجی را از [`config/latentbox/tools.yaml`](config/latentbox/tools.yaml) بارگیری می‌کند و نقاط پایانی همگام‌سازی/جست‌وجو را در کنار رابط‌های کنسول ارائه می‌دهد.

## امنیت، به‌روزرسانی و انطباق

- اولین بوت `apt-get update && apt-get upgrade` و `snap refresh` را اجرا می‌کند، سپس سرویس‌های مخصوص پروفایل را نصب می‌کند؛ لاگ‌ها در `/var/log/aionos-firstboot.log` ذخیره می‌شوند.
- Secure Boot، رمزگذاری کامل دیسک و سخت‌سازی CIS-lite در [`docs/security`](docs/security) همراه با برنامه به‌روزرسانی و ردیابی CVE مستند شده‌اند.
- جریان‌های نصاب اقدامات مخرب را پشت `AIONOS_ALLOW_INSTALL` محافظت می‌کنند و گام‌های SBOM/امضای توضیح داده‌شده در [`docs/release.md`](docs/release.md) را اجرا می‌کنند.

## سازگاری سخت‌افزاری

ماتریس‌های سازگاری (GPU، NIC، وای‌فای، میان‌افزار) و فرآیند گزارش در [`docs/hcl`](docs/hcl) موجود است. اسکریپت‌های تشخیص در `core/installer/bridge/tasks` بررسی سخت‌افزار را خودکار می‌کنند.

## مرکز مستندات

راهبردهای عملیاتی سازمانی از [`docs/README.md`](docs/README.md) آغاز می‌شوند: راهنمای شروع سریع، حالت‌های نصب، پروفایل‌ها، پایه‌های امنیتی، عیب‌یابی، انتشار، حریم خصوصی و سازگاری سخت‌افزاری.

## مشارکت و مجوز

پیش از ارسال تغییرات، [CONTRIBUTING.md](CONTRIBUTING.md)، [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) و [SECURITY.md](SECURITY.md) را مرور کنید. آیون‌اواس تحت [مجوز آپاچی ۲٫۰](LICENSE) منتشر شده است.
