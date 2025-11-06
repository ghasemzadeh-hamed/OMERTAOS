
---

```markdown
# AION-OS (OMERTAOS)
پلتفرم ماژولار ارکستراسیون ایجنت‌های هوش مصنوعی؛ شامل **Gateway (Node/TypeScript)**، **Control Plane (FastAPI/Python)**، **Console (Next.js)**، هسته‌های اجرا و **ماژول‌های Rust**، به‌همراه ابزارهای استقرار (Docker Compose) و اسناد مشارکت/امنیت.

[Apache-2.0](LICENSE) • Cross-Lang (TS/Python/Rust) • Docker-first • Native Install

---

## فهرست مطالب
- [معرفی](#معرفی)
- [ویژگی‌ها](#ویژگی‌ها)
- [معماری](#معماری)
- [نقشهٔ مخزن (Repository Map)](#نقشهٔ-مخزن-repository-map)
- [پیش‌نیازها](#پیش‌نیازها)
- [پیکربندی (Environment)](#پیکربندی-environment)
- [راه‌اندازی سریع با Docker Compose](#راهاندازی-سریع-با-docker-compose)
  - [پروفایل پایه](#پروفایل-پایه)
  - [پروفایل vLLM / سروینگ مدل](#پروفایل-vllm--سروینگ-مدل)
  - [پروفایل Observability](#پروفایل-observability)
  - [دستورهای مدیریت](#دستورهای-مدیریت)
- [نصب و اجرای بومی (Native)](#نصب-و-اجرای-بومی-native)
  - [Linux / macOS](#linux--macos)
  - [Windows (PowerShell)](#windows-powershell)
- [اجرای سرویس‌ها به‌صورت دستی (بدون کانتینر)](#اجرای-سرویسها-بهصورت-دستی-بدون-کانتینر)
  - [Control Plane (FastAPI)](#control-plane-fastapi)
  - [Gateway (TypeScript/Node)](#gateway-typescriptnode)
  - [Console (Nextjs)](#console-nextjs)
  - [ماژول‌های Rust](#ماژولهای-rust)
- [API ها و نقاط سلامت](#api-ها-و-نقاط-سلامت)
- [تست، کیفیت کد و CI](#تست-کیفیت-کد-و-ci)
- [عیب‌یابی (Troubleshooting)](#عیبیابی-troubleshooting)
- [امنیت، مجوز، مشارکت و حاکمیت](#امنیت-مجوز-مشارکت-و-حاکمیت)
- [FAQ](#faq)

---

## معرفی
AION-OS (یا OMERTAOS) یک بستر ماژولار برای ساخت و اجرای **ایجنت‌ها** و **جریان‌های کاری هوش مصنوعی** است. معماری چندزبانه آن به شما امکان می‌دهد در لایهٔ ورودی، کنترل و اجرای وظایف از مناسب‌ترین زبان و ابزار استفاده کنید. ساختار ریپو شامل دایرکتوری‌های **gateway**, **control**, **console**, **modules**, **kernel**، و فایل‌های Compose برای سناریوهای مختلف است. :contentReference[oaicite:1]{index=1}

---

## ویژگی‌ها
- معماری تفکیک‌شده: Gateway (ورودی/مسیر‌یابی)، Control Plane (حکم‌رانی/هماهنگی)، Execution Modules (اجرا)
- چندزبانه (TS/Python/Rust) با تمرکز بر عملکرد و توسعه‌پذیری
- توسعهٔ محلی و استقرار سریع با **Docker Compose** (پروفایل‌های base / vLLM / observability) :contentReference[oaicite:2]{index=2}
- پشتیبانی از **Console (Next.js)** برای UI مدیریتی
- الگوهای استاندارد برای Agentها، رجیستری هوش مصنوعی، و اسکیماهای کانفیگ
- اسناد و سیاست‌های امنیتی/مشارکت (CODE_OF_CONDUCT, CONTRIBUTING, GOVERNANCE, SECURITY) در ریشهٔ ریپو :contentReference[oaicite:3]{index=3}

---

## معماری
جریان کلّی:
```

[ Client / Tools / Console ] --> [ Gateway (Node/TS) ] --> [ Control Plane (FastAPI) ]
|                     |
|                     +--> [ Policies / Workflows / Registry ]
+--> [ Modules (Rust) ]----> [ Task Runners / Inference / IO ]

+--> [ External Services (DB/Cache/Vector/Queues) ]

```
- **Gateway** مسئول احراز، مسیردهی و API Aggregation.
- **Control Plane** مسئول سیاست‌ها، ارکستراسیون، و هماهنگی جریان‌ها.
- **Modules (Rust)** اجرای محاسبات/Inference/IO با کارایی بالا.
- **Console** رابط وب برای مانیتورینگ، تنظیمات و اجراهای تعاملی.

---

## نقشهٔ مخزن (Repository Map)

```

OMERTAOS/
├─ .aionos/                   # پیکربندی‌های داخلی پروژه
├─ .github/                   # قالب‌های Issue/PR و اکشن‌ها
├─ agents/                    # قالب‌ها/نمونه‌های Agent
├─ ai_registry/               # رجیستری مؤلفه‌ها/مدل‌ها
├─ bigdata/                   # اجزای پردازش داده حجیم
├─ cli/                       # ابزار خط فرمان
├─ config-schemas/            # اسکیماهای یکنواخت برای کانفیگ
├─ config/ , configs/         # کانفیگ‌های اجرای سرویس‌ها
├─ console/                   # کنسول وب (Next.js)
├─ control/                   # Control Plane (FastAPI/Python)
├─ deploy/                    # فایل‌ها/اسکریپت‌های استقرار
├─ execution/                 # لایه‌های اجرای وظیفه
├─ explorer/                  # ابزارهای اکتشافی/دیباگ
├─ gateway/                   # API Gateway (TypeScript/Node)
├─ kernel/ , kernel-multitenant/   # هستهٔ اجرا (تک/چند مستاجر)
├─ modules/                   # ماژول‌های Rust (اجرا/درایورها)
├─ policies/                  # سیاست‌ها/قوانین/Workflowها
├─ profiles/                  # پروفایل‌ها/تمپلیت‌های اجرا
├─ protos/aion/v1/            # پروتکل‌ها/تعاریف (gRPC/Proto)
├─ schemas/                   # اسکیماهای داده
├─ scripts/                   # اسکریپت‌های کمکی (ساخت/دیپلوی)
├─ test/ , tests/             # تست‌های واحد/یکپارچه
├─ tools/ , typer/            # ابزارها و ماژول‌های تایپی
│
├─ docker-compose.yml         # پروفایل پایه سرویس‌ها
├─ docker-compose.vllm.yml    # سروینگ مدل با vLLM
├─ docker-compose.obsv.yml    # Observability stack
├─ docker-compose.local.yml   # تنظیمات محلی/توسعه
│
├─ .editorconfig  .gitignore  .pre-commit-config.yaml
├─ .env.example               # نمونهٔ متغیرهای محیطی
├─ Makefile                   # اهداف ساخت/تست/کمک
├─ install.sh / uninstall.sh  # نصب/حذف برای Unix
├─ install.ps1 / uninstall.ps1
├─ install_all_win.ps1
├─ requirements.txt
├─ CODE_OF_CONDUCT.md  CONTRIBUTING.md  GOVERNANCE.md  SECURITY.md
└─ LICENSE

````
> مسیرها و فایل‌ها بر اساس فهرست ریپو گردآوری شده‌اند. :contentReference[oaicite:4]{index=4}

---

## پیش‌نیازها
- **Git**
- **Node.js 18+** (برای Gateway و Console)
- **Python 3.10+** (برای Control Plane)
- **Rust + Cargo** (برای ماژول‌های اجرایی)
- **Docker / Docker Compose** (برای استقرار سریع – توصیه‌شده)
- دسترسی به منابع محلی/شبکه برای پایگاه‌داده‌ها، کش، یا سرویس‌های خارجی (در صورت نیاز)

---

## پیکربندی (Environment)
۱) یک فایل پیکربندی بسازید:
```bash
cp .env.example .env
````

۲) کلیدهای متداول (بنا به نیاز پروژه):

```
# شبکه و پورت‌ها
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8080
CONTROL_HOST=0.0.0.0
CONTROL_PORT=8000
CONSOLE_PORT=3000

# سرویس‌های خارجی
DATABASE_URL=postgres://user:pass@host:5432/db
REDIS_URL=redis://host:6379
VECTOR_DB_URL=http://qdrant:6333     # یا Milvus/Weaviate ...
MESSAGE_BROKER_URL=nats://host:4222  # یا Kafka/RabbitMQ ...

# مدل/رجیستری
MODEL_REGISTRY_PATH=./ai_registry
MODULES_PATH=./modules

# لاگ/امنیت
LOG_LEVEL=info
JWT_SECRET=change_me
CORS_ORIGINS=*
```

> مقادیر پیش‌فرض را مطابق نیاز محیط خود اصلاح کنید. نمونهٔ `.env.example` در ریشه موجود است. ([GitHub][1])

---

## راه‌اندازی سریع با Docker Compose

### پروفایل پایه

در ریشهٔ پروژه:

```bash
docker compose -f docker-compose.yml up -d
```

* سرویس‌ها در پس‌زمینه بالا می‌آیند.
* برای مشاهدهٔ وضعیت/لاگ:

```bash
docker compose ps
docker compose logs -f
```

* توقف/پاکسازی:

```bash
docker compose down
```

> فایل `docker-compose.yml` در ریشه موجود است. ([GitHub][1])

### پروفایل vLLM / سروینگ مدل

برای راه‌اندازی سروینگ مدل (LLM) با vLLM:

```bash
docker compose -f docker-compose.vllm.yml up -d
```

* متغیرهای مرتبط با مسیر مدل/توکن‌ها را در `.env` ست کنید (مثلاً `VLLM_MODEL`, `HF_TOKEN`).
* ادغام با Control Plane/Gateway از طریق آدرس‌های داخلی Compose انجام می‌شود.

> فایل `docker-compose.vllm.yml` موجود است. ([GitHub][1])

### پروفایل Observability

برای فعال‌سازی پایش و مشاهده‌پذیری (metrics/logs/traces):

```bash
docker compose -f docker-compose.obsv.yml up -d
```

* سرویس‌هایی مثل Grafana/Prometheus/Loki/Tempo (بسته به فایل) بالا می‌آیند.
* داشبوردها را با آدرس‌های تعریف‌شده در Compose بررسی کنید.

> فایل `docker-compose.obsv.yml` موجود است. ([GitHub][1])

### دستورهای مدیریت

سناریوهای رایج:

```bash
# اجرای همزمان چند پروفایل
docker compose \
  -f docker-compose.yml \
  -f docker-compose.vllm.yml \
  -f docker-compose.obsv.yml up -d

# توقف بدون حذف volumeها
docker compose down

# توقف و حذف volumeها (پاکسازی کامل)
docker compose down --volumes --remove-orphans

# مشاهده لاگ یک سرویس خاص
docker compose logs -f control
docker compose logs -f gateway
docker compose logs -f console
```

---

## نصب و اجرای بومی (Native)

### Linux / macOS

روش خودکار:

```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
./install.sh
```

روش دستی (سطرهای کلیدی):

```bash
# 1) ساخت پوشه‌های خروجی و نصب پیش‌نیازها (در صورت نیاز)

# 2) نصب پکیج‌های Python برای Control Plane
cd control
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r ../requirements.txt
# یا اگر در control/ فایل req جداگانه دارید همان را نصب کنید
cd ..

# 3) نصب پکیج‌های Node برای Gateway و Console
cd gateway && npm install && cd ..
cd console && npm install && cd ..

# 4) ساخت ماژول‌های Rust
cd modules
cargo build --release
cd ..

# 5) تنظیم متغیرها
cp .env.example .env
# ویرایش .env و پورت‌ها/URL ها را ست کنید

# 6) اجرای سرویس‌ها (در ترمینال‌های جداگانه یا با tmux)
#   - Control Plane
#   - Gateway
#   - Console
#   - ماژول‌ها (در صورت نیاز به اجرای جداگانه)
```

حذف (در صورت نیاز):

```bash
./uninstall.sh
```

> اسکریپت‌های نصب/حذف در ریشه موجودند. ([GitHub][1])

### Windows (PowerShell)

روش خودکار:

```powershell
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS
.\install_all_win.ps1
```

روش دستی (خلاصهٔ گام‌ها):

```powershell
# Python venv + pip install -r requirements.txt
# npm install در gateway/ و console/
# cargo build --release در modules/
# کپی و ویرایش .env
# اجرای uvicorn برای control، npm scripts برای gateway/console
```

حذف:

```powershell
.\uninstall.ps1
```

> اسکریپت‌های PowerShell در ریشه موجودند. ([GitHub][1])

---

## اجرای سرویس‌ها به‌صورت دستی (بدون کانتینر)

### Control Plane (FastAPI)

```bash
cd control
# فرض app:app به‌عنوان ASGI
uvicorn app:app --host 0.0.0.0 --port ${CONTROL_PORT:-8000} --reload
# مستندات: http://localhost:8000/docs  (Swagger UI)
```

### Gateway (TypeScript/Node)

```bash
cd gateway
npm run build      # در صورت وجود
npm run start      # یا npm run dev
# پیش‌فرض: http://localhost:${GATEWAY_PORT:-8080}
```

### Console (Next.js)

```bash
cd console
npm run dev        # توسعه
# یا npm run build && npm start  (Production)
# پیش‌فرض: http://localhost:${CONSOLE_PORT:-3000}
```

### ماژول‌های Rust

```bash
cd modules
cargo build --release
# اگر باینری/سرویس جداگانه دارید، مستقیم اجرا کنید
# ./target/release/<module-binary> --config ./config/<file>.yaml
```

---

## API ها و نقاط سلامت

* **Gateway**

  * `GET /health` → وضعیت سرویس Gateway
  * مسیرهای Proxy/Aggregation برای Control Plane/Modules
* **Control Plane (FastAPI)**

  * `GET /health` → وضعیت Control Plane
  * `GET /docs` و `GET /openapi.json` → مستندات خودکار Swagger/OpenAPI
* **Console**

  * مسیر پایه UI: `/` روی پورتی که در `.env` مشخص کرده‌اید

> پورت‌ها با `.env` قابل سفارشی‌سازی‌اند. فایل‌های سرویس در `gateway/`, `control/`, `console/` قرار دارند. ([GitHub][1])

---

## تست، کیفیت کد و CI

* Python:

  ```bash
  cd control
  pytest -q
  ruff check .         # در صورت استفاده از Ruff/Flake8
  mypy .               # در صورت استفاده از Type Hints
  ```
* Node/TypeScript:

  ```bash
  cd gateway
  npm test
  npm run lint         # eslint
  ```
* Rust:

  ```bash
  cd modules
  cargo test
  cargo clippy --all-targets --all-features -- -D warnings
  cargo fmt -- --check
  ```
* Git Hooks / Pre-commit:

  * پیکربندی در `.pre-commit-config.yaml` موجود است؛ فعال‌سازی:

    ```bash
    pre-commit install
    pre-commit run --all-files
    ```
* CI (GitHub Actions):

  * قالب‌ها/ورک‌فلوها در `.github/` قرار دارند. ([GitHub][1])

---

## عیب‌یابی (Troubleshooting)

* **پورت‌ها مشغول هستند**: پورت‌ها را در `.env` تغییر دهید یا سرویس‌های قبلی را متوقف کنید.
* **Console/Gateway به Control دسترسی ندارند**: آدرس/پورت داخلی یا نام سرویس در Docker Compose را بررسی کنید.
* **ماژول‌های Rust پیدا نمی‌شوند**: `MODULES_PATH` را تنظیم کرده و `cargo build --release` را اجرا کنید.
* **OpenAPI در دسترس نیست**: مطمئن شوید `uvicorn` با اپ صحیح (مثلاً `app:app`) بالا آمده باشد.
* **Latency بالا**: لاگ‌ها و متریک‌ها را در پروفایل Observability بررسی کنید؛ منابع محاسباتی vLLM/مدل را افزایش دهید.

---

## امنیت، مجوز، مشارکت و حاکمیت

* **امنیت**: دستورالعمل‌ها در [`SECURITY.md`](SECURITY.md)
* **کد اخلاق**: [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
* **راهنمای مشارکت**: [`CONTRIBUTING.md`](CONTRIBUTING.md)
* **حاکمیت پروژه**: [`GOVERNANCE.md`](GOVERNANCE.md)
* **مجوز**: [`LICENSE`](LICENSE) (Apache-2.0)

> همهٔ این فایل‌ها در ریشهٔ پروژه موجود است. ([GitHub][1])

---

## FAQ

**❓ آیا فقط با Docker اجرا می‌شود؟**
خیر. اسکریپت‌های نصب/اجرای بومی برای Linux/macOS (`install.sh`) و Windows (`install_all_win.ps1`) فراهم است. ([GitHub][1])

**❓ آیا می‌توان از مدل دلخواه استفاده کرد؟**
بله. با پروفایل `docker-compose.vllm.yml` یا تنظیم end-point سروینگ مدل خود، می‌توانید LLM دلخواه را متصل کنید. ([GitHub][1])

**❓ Observability چگونه فعال می‌شود؟**
پروفایل `docker-compose.obsv.yml` را بالا بیاورید و به داشبوردهای از پیش‌تعریف‌شده مراجعه کنید. ([GitHub][1])

**❓ کجا ساختار Agent/Policy را تغییر دهم؟**
دایرکتوری‌های `agents/` و `policies/` و اسکیماهای مرتبط در `config-schemas/` و `schemas/`. ([GitHub][1])

---

## نشان‌گرهای مفید (Cheatsheet)

```bash
# ساخت فایل env
cp .env.example .env

# Docker پایه
docker compose -f docker-compose.yml up -d
docker compose logs -f control

# vLLM
docker compose -f docker-compose.vllm.yml up -d

# Observability
docker compose -f docker-compose.obsv.yml up -d

# توقف و پاکسازی
docker compose down --volumes --remove-orphans
```

---

> برای هرگونه بهینه‌سازی (Dev/Prod)، اتصال به دیتابیس/کش/پیام‌رسان، و سفارشی‌سازی لایهٔ اجرا، مقداردهی `.env` و Compose را مطابق زیرساخت خودتان تنظیم کنید.

```

---


::contentReference[oaicite:18]{index=18}
```

[1]: https://github.com/Hamedghz/OMERTAOS "GitHub - Hamedghz/OMERTAOS: aionOS is a modular AI orchestration platform combining a TypeScript gateway, FastAPI control plane, and Rust execution modules."
