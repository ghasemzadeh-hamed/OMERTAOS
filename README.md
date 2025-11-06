# AION-OS (OMERTAOS)
**یک پلتفرم ماژولار برای ارکستراسیون ایجنت‌های هوش مصنوعی**؛ شامل **Gateway (Node/TypeScript)**، **Control Plane (FastAPI/Python)**، **Console (Next.js)** به‌همراه هستهٔ اجرا و ماژول‌ها، ابزارهای استقرار (Docker Compose)، و مستندات نصب بومی (Native).  [oai_citation:0‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## فهرست
- [معرفی](#معرفی)
- [کارایی‌ها (Use-Cases & Capabilities)](#کاراییها-usecases--capabilities)
- [ساختار معماری و لایه‌ها](#ساختار-معماری-و-لایهها)
- [نقشهٔ مخزن (Repository Map)](#نقشهٔ-مخزن-repository-map)
- [ارتباطات بین اقسام (Interactions)](#ارتباطات-بین-اقسام-interactions)
- [کلیدهای فنی و کانفیگ](#کلیدهای-فنی-و-کانفیگ)
- [راهنمای نصب و راه‌اندازی](#راهنمای-نصب-و-راهاندازی)
  - [Quick Setup & Start (Docker Compose)](#quick-setup--start-docker-compose)
  - [File Configuration Setup](#file-configuration-setup)
  - [نصب بومی (Native / No Docker)](#نصب-بومی-native--no-docker)
  - [Windows (PowerShell) و Linux](#windows-powershell-و-linux)
  - [سیستم خام (Fresh OS prerequisites)](#سیستم-خام-fresh-os-prerequisites)
  - [وب‌اواس (Web UI) و ترمینال (Headless)](#وباواس-web-ui-و-ترمینال-headless)
- [توسعه، تست و MLOps](#توسعه-تست-و-mlops)
- [امنیت و عملیات](#امنیت-و-عملیات)
- [مجوز](#مجوز)

---

## معرفی
AION-OS یک بستر **قابل‌گسترش و چندلایه** برای ساخت، اجرای ایمن و پایش‌پذیر ایجنت‌های هوش مصنوعی است. این مخزن، سرویس‌های **Gateway** (مسیریابی و ورودی)، **Control Plane** (سیاست‌گذاری/هماهنگی)، **Console** (رابط وب) و اجزای اجرا/ماژول‌ها را در خود دارد و با **Docker Compose** و اسکریپت‌های نصب **Linux/Windows** ارائه می‌شود. همچنین راهنمای «نصب بومی (بدون داکر)» در `docs/INSTALL_native.md` آمده است.  [oai_citation:1‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## کارایی‌ها (Use-Cases & Capabilities)
- **اجرای چندمسیرهٔ ایجنت‌ها**: هدایت درخواست‌ها به اجراهای محلی، سرویس‌های ابری یا حالت‌های هیبرید.
- **کنترل متمرکز**: سیاست‌ها، بودجه‌ها/سقف هزینه، SLA و ردیابی درخواست.
- **قابلیت مشاهده‌پذیری (Observability)**: لاگ، متریک و تریس برای عملیات در مقیاس (پوشهٔ `bigdata/`).  [oai_citation:2‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **قراردادها/اسکیما**: قراردادهای پروتوباف در `protos/aion/v1`، اسکیماها در `schemas/` و نمونه‌کانفیگ‌ها در `config-schemas/`.  [oai_citation:3‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **توسعهٔ محصول و ML-Guard**: Makefile و سیاست‌های آموزشی در `policies/`؛ دستورهای `make setup / make train / make guard` برای آموزش/کنترل بیش‌برازش و تولید آرتیفکت‌های قابل تکرار.  [oai_citation:4‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## ساختار معماری و لایه‌ها
**لایه‌ها و مسئولیت‌ها:**
- **Gateway (ورودی/مرزبانی)**  
  مسیریابی درخواست‌های کلاینت (HTTP/WS و …)، احراز هویت/نرخ‌دهی و اعمال سیاست‌های اولیه. پیاده‌سازی با Node.js/TypeScript (پوشهٔ `gateway/`).  [oai_citation:5‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Control Plane (هماهنگی/سیاست‌گذاری)**  
  سرویس FastAPI برای تصمیم‌گیری مسیر اجرا، مدیریت وضعیت، ارکستراسیون ماژول‌ها و اینتنت‌ها (پوشهٔ `control/`).  [oai_citation:6‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Execution Kernel & Modules**  
  هستهٔ اجرا و ماژول‌ها (پوشه‌های `kernel/`, `kernel-multitenant/`, `execution/`, `modules/`) برای پردازش واقعی وظایف ایجنت.  [oai_citation:7‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Console (رابط وب)**  
  برنامهٔ Next.js برای مشاهدهٔ زندهٔ وضعیت سرویس‌ها، رخدادها و مدیریت (پوشهٔ `console/`).  [oai_citation:8‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Data/Observability Plane**  
  اجزای پایش/کلان‌داده در `bigdata/` و یکپارچه‌سازی با Compose استک‌های جداگانه.  [oai_citation:9‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Contracts & Schemas**  
  پروتکل‌های پیام (gRPC/Protobuf) در `protos/aion/v1`، اسکیماها در `schemas/` و نمونه‌فایل‌های کانفیگ در `config-schemas/`.  [oai_citation:10‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Policy & Profiles**  
  سیاست‌ها و پروفایل‌ها در `policies/` و `profiles/` برای کنترل رفتار سامانه.  [oai_citation:11‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## نقشهٔ مخزن (Repository Map)
> مهم‌ترین دایرکتوری‌ها بر اساس ساختار کد:  [oai_citation:12‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- `.aionos/` — قراردادها/Artifacts داخلی پروژه.  
- `.github/` — ورک‌فلوها و کانفیگ‌های گیت‌هاب اکشنز.  
- `agents/` & `templates/` — تمپلیت‌های ساخت ایجنت/تعاریف نمونه.  
- `ai_registry/` — رجیستری/تعاریف Provider/Model.  
- `bigdata/` — استک اختیاری برای لاگ/رویداد/تحلیل.  
- `cli/` & `typer/` — ابزار CLI و چارچوب فرمان (مبتنی بر Typer در پایتون).  
- `config/`, `configs/`, `config-schemas/` — کانفیگ‌های نمونه و طرحواره‌ها.  
- `console/` — وب‌اپ Next.js (پنل مدیریتی).  
- `control/` — سرویس FastAPI (کنترل پلین).  
- `execution/`, `kernel/`, `kernel-multitenant/`, `modules/` — اجزای اجرا و ماژول‌ها.  
- `explorer/` — ابزار اکتشاف/دیباگ.  
- `gateway/` — سرویس ورودی Node/TypeScript.  
- `policies/`, `profiles/` — سیاست‌ها و پروفایل‌ها (از جمله `policies/training.yaml`).  
- `protos/aion/v1/` — قراردادهای Protobuf/gRPC.  
- `schemas/` — اسکیماهای داده و اعتبارسنجی.  
- `scripts/`, `tools/` — اسکریپت‌ها و ابزار توسعه/عملیات.  
- `test/`, `tests/` — تست‌های واحد و یکپارچه.  
- ریشهٔ مخزن: `Makefile`, `requirements.txt`, `docker-compose*.yml`, `install.sh`, `install.ps1`, `install_all_win.ps1`, `uninstall.*`, `.env.example`.  [oai_citation:13‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## ارتباطات بین اقسام (Interactions)
- **Client → Gateway**: دریافت درخواست‌ها، احراز هویت، محدودسازی نرخ و مسیریابی اولیه.  
- **Gateway → Control Plane**: ارسال متادادهٔ درخواست/اینتنت و درخواست تصمیم مسیر اجرا.  
- **Control Plane ↔ Kernel/Modules**: واگذاری اجرا، اعمال سیاست‌ها/سهمیه‌ها، دریافت نتایج.  
- **Console ↔ Gateway/Control**: خواندن وضعیت سلامت، لاگ‌ها و ایونت‌ها برای نمایش.  
- **Observability Stack ↔ همهٔ سرویس‌ها**: انتشار متریک/تریس/لاگ به استک کلان‌داده.  
- **Contracts (protos) ↔ سرویس‌ها**: تبادل ساخت‌یافتهٔ پیام‌ها مبتنی بر قراردادهای `protos/aion/v1`.  [oai_citation:14‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## کلیدهای فنی و کانفیگ
> فایل نمونه‌ی محیطی در ریشهٔ مخزن: `.env.example` (برای آغاز تنظیمات). همچنین چند Compose Stack در `docker-compose.yml`, `docker-compose.local.yml`, `docker-compose.obsv.yml`, `docker-compose.vllm.yml` وجود دارد.  [oai_citation:15‡GitHub](https://github.com/Hamedghz/OMERTAOS)

**راهنمای کلی تنظیمات:**
- **فایل‌های محیطی (.env)**: پورت‌ها، هاست/بایندینگ، کلیدهای دسترسی Providerها، تنظیمات TLS/MTLS، حالت چندسازمانی/چندگانگی (tenancy) و …  
- **Policy & Profiles**: تنظیم اینتنت‌ها، بودجه‌ها، SLAها، محدودیت‌ها و تنظیمات آموزش/Guard در `policies/` (از جمله `policies/training.yaml`).  [oai_citation:16‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Schemas & Config-schemas**: برای اعتبارسنجی و تولید کانفیگ‌ها.  [oai_citation:17‡GitHub](https://github.com/Hamedghz/OMERTAOS)
- **Compose Stacks**: استک پایه، استک محلی (local dev)، استک Observability و استک مبتنی بر vLLM/GPU (در صورت وجود GPU).  [oai_citation:18‡GitHub](https://github.com/Hamedghz/OMERTAOS)

> **نکتهٔ مهم:** نام و مقدار کلیدها را از **`.env.example`** و یادداشت‌های داخل هر Compose Stack استخراج کنید و سپس نیازهای محیط خود را اعمال نمایید.  [oai_citation:19‡GitHub](https://github.com/Hamedghz/OMERTAOS)

---

## راهنمای نصب و راه‌اندازی

### Quick Setup & Start (Docker Compose)
1) دریافت کد:
```bash
git clone https://github.com/Hamedghz/OMERTAOS.git
cd OMERTAOS

	2.	آماده‌سازی فایل‌های محیطی:

cp .env.example .env
# (مقادیر را طبق محیط خودتان و سرویس‌ها تکمیل کنید)

	3.	اجرای استک پایه با Docker Compose:

docker compose up -d
docker compose ps

	4.	(اختیاری) فعال‌سازی استک Observability یا GPU (در صورت نیاز):

# Observability / Big Data
docker compose -f docker-compose.obsv.yml up -d

# vLLM/GPU
docker compose -f docker-compose.vllm.yml up -d

	5.	مشاهده لاگ‌ها و سلامت سرویس‌ها:

docker compose logs -f
# برای سرویس خاص:
docker compose logs -f control
docker compose logs -f gateway
docker compose logs -f console

فایل‌های Compose و اسکریپت‌های نصب/حذف در ریشه موجودند: docker-compose*.yml, install.sh, install.ps1, install_all_win.ps1, uninstall.*.  ￼

⸻

File Configuration Setup
	•	.env: پورت‌ها/هاست، کلیدهای Provider (LLM/بردار/ذخیره‌ساز)، پرچم‌های امنیتی (TLS/MTLS)، تنظیمات چنداجاره‌ای (tenancy) و … را تکمیل کنید. (نمونه: .env.example)  ￼
	•	policies/:
	•	training.yaml برای سیاست‌های آموزشی/Guard (تقسیم داده، Cross-Val، Early-Stopping، Ensemble، Feature-Selection و …).  ￼
	•	config-schemas/, schemas/: اسکیماها/طرحواره‌ها برای تولید و اعتبارسنجی کانفیگ.  ￼
	•	docker-compose*.yml: درگاه‌ها/وابستگی‌ها/ولوم‌ها را مطابق محیط تان اصلاح کنید.  ￼

⸻

نصب بومی (Native / No Docker)

پروژه راهنمای نصب بومی (بدون داکر) را در docs/INSTALL_native.md فراهم کرده است. این راهنما مراحل Linux و Windows، نصاب‌های خودکار، مدیریت سرویس‌های سیستمی و Smoke Test را پوشش می‌دهد. اگر قصد اجرای مستقیم سرویس‌ها روی میزبان را دارید، این سند را دنبال کنید.  ￼

پیش‌نیازهای پیشنهادی برای نصب بومی:
	•	Node.js (LTS) برای gateway/ و console/
	•	Python 3.11+ برای control/ (به‌همراه requirements.txt)  ￼
	•	Rust/Cargo برای بخش‌های کرنل/ماژول‌هایی که به Rust متکی‌اند
	•	ابزارهای Build (gcc/clang, make, git)

⸻

Windows (PowerShell) و Linux
	•	Linux:
از اسکریپت ریشه استفاده کنید:

./install.sh
# حذف سرویس‌ها:
./uninstall.sh

￼

	•	Windows:
با PowerShell اجرا کنید:

powershell -ExecutionPolicy Bypass -File .\install.ps1
# نصب کامل همه اجزا:
powershell -NoProfile -ExecutionPolicy Bypass -File .\install_all_win.ps1
# حذف:
powershell -ExecutionPolicy Bypass -File .\uninstall.ps1

￼

در هر دو سیستم‌عامل می‌توانید به‌جای اسکریپت‌ها از Docker Compose یا نصب بومی طبق docs/INSTALL_native.md استفاده کنید.  ￼

⸻

سیستم خام (Fresh OS prerequisites)
	1.	نصب Git, Docker Engine و Docker Compose v2 (برای مسیر Compose).
	2.	نصب Node.js LTS و Python 3.11+ و Rust (برای مسیر نصب بومی).
	3.	کلون مخزن و دنبال‌کردن یکی از مسیرها: Compose یا Native.

مراجع: وجود requirements.txt, docker-compose*.yml و سند نصب بومی.  ￼

⸻

وب‌اواس (Web UI) و ترمینال (Headless)
	•	Web UI (Console): پس از بالا آمدن سرویس‌ها با Compose/Native، سرویس Console اجرا می‌شود (پوشهٔ console/). با مرورگر به آدرس/پورتی که در .env یا Compose تعیین شده مراجعه کنید و وضعیت سرویس‌ها را مشاهده کنید.  ￼
	•	Headless / Terminal:
	•	بررسی سرویس‌ها:

docker compose ps
docker compose logs -f control


	•	تست سلامت (نمونهٔ عمومی):

# بررسی endpoint سلامت هر سرویس در پورتی که پیکربندی کرده‌اید:
curl -sf http://127.0.0.1:<PORT>/health || true


	•	اکتشاف/دیباگ از طریق ابزارهای cli/ یا explorer/. (پوشه‌ها در مخزن موجودند.)  ￼

⸻

توسعه، تست و MLOps
	•	Makefile: دستورات آماده برای راه‌اندازی محیط، آموزش و Guard:

make setup
make train
make guard

این فرایند از سیاست‌های policies/training.yaml پیروی می‌کند و آرتیفکت‌ها (متریک/کانفیگ/اهمیت ویژگی‌ها) را در پوشهٔ artifacts/ ذخیره می‌کند تا تکرارپذیری تضمین شود. همچنین در CI با GitHub Actions جریان model-check (طبق توضیح README مخزن) اجرا می‌شود و در صورت نقض آستانه‌ها شکست می‌خورد.  ￼

	•	پوشه‌های test/ و tests/ برای تست‌ها فراهم است.  ￼
	•	Contracts & Schemas: تغییرات API را همزمان در protos/ و schemas/ نگه دارید.  ￼

⸻

امنیت و عملیات
	•	SECURITY.md و GOVERNANCE.md در ریشهٔ مخزن موجود است—برای سیاست‌های امنیتی و حاکمیت مطالعه شود.  ￼
	•	استفاده از متغیرهای محیطی امن در .env (هرگز به Git متعهد نکنید) و سیگنال‌های سلامت/آمادگی برای مانیتورینگ خارجی.
	•	Observability Stack (اختیاری): با استک bigdata/ و Compose مربوطه متریک/تریس/لاگ را جمع‌آوری کنید.  ￼

⸻

مجوز

این پروژه تحت مجوز Apache-2.0 منتشر شده است. فایل LICENSE در ریشهٔ مخزن قرار دارد.  ￼

⸻

پیوست: نکات عملی پیشنهاد‌شده
	•	تنظیم .env از روی .env.example و سپس اجرای docker compose up -d—ساده‌ترین مسیر اجرا.  ￼
	•	برای Native، قبل از هر چیز سند docs/INSTALL_native.md را دنبال کنید (به‌ویژه نصب وابستگی‌ها و مدیریت سرویس‌ها).  ￼
	•	در صورت اجرای GPU، استک docker-compose.vllm.yml را بررسی و فعال کنید (درایور/Toolkit باید نصب باشد).  ￼

> اگر بخواهی، نسخهٔ انگلیسی همین README را هم آماده می‌کنم—و همچنین یک **checklist کانفیگ** (قابل پرینت) برای Dev/Stage/Prod تا هر انتشار بدون نقص بالا بیاید.
