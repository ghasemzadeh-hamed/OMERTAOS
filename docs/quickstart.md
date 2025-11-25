# Quick start

This guide condenses each supported deployment into ten steps or fewer. Run every command as root or with `sudo` unless noted.

## Containerized quick start

### Linux (Docker Engine)

1. Install Git, Docker Engine 24+ with the Compose plugin, and Python 3.11 or newer.
2. Clone the repository: `git clone https://github.com/Hamedghz/OMERTAOS.git && cd OMERTAOS`.
3. Execute the wrapper: `./install.sh --profile user` (substitute `professional` or `enterprise-vip` as needed).
4. Add `--local` to target [`docker-compose.local.yml`](../docker-compose.local.yml) for lightweight developer profiles.
5. Use `--update` when you want the script to fetch the latest commits before launching services.
6. Watch [`scripts/quicksetup.sh`](../scripts/quicksetup.sh) preflight checks and compose startup; `.env` is rendered automatically from [`config/templates/.env.example`](../config/templates/.env.example) if missing.
7. Open the console at `http://localhost:3000` and complete the onboarding wizard.
8. Verify service health from the dashboard (`Control`, `Gateway`, `Console` tiles should show green).
9. When finished, run `docker compose down` to stop the stack.

### Windows 11 / WSL2

1. Install Git for Windows, Docker Desktop (WSL integration enabled), and PowerShell 7+.
2. Clone the repository: `git clone https://github.com/Hamedghz/OMERTAOS.git`.
3. From an elevated PowerShell prompt in the repository root, run `pwsh ./install.ps1 -Profile user` (or `professional` / `enterprise-vip`).
4. Append `-Local` for the developer overlay or `-Update` to pull fresh commits before launching containers.
5. The script orchestrates [`docker-compose.yml`](../docker-compose.yml) via [`scripts/quicksetup.ps1`](../scripts/quicksetup.ps1); watch the output for prerequisite warnings.
6. When prompted, sign in to Docker Desktop so the compose project can start.
7. Open `http://localhost:3000` from Windows to finish the wizard.
8. Stop the environment with `docker compose down` (PowerShell) when you are done testing.

## ISO / Kiosk

1. Fetch the latest release artifact from the release bucket and verify the checksum (see [`docs/release.md`](release.md)).
2. Write the ISO to a USB drive (`dd if=aionos.iso of=/dev/sdX bs=4M status=progress`).
3. Boot the target system with Secure Boot enabled if supported.
4. When the kiosk launches, confirm networking and press **Start Installer**.
5. Select locale, keyboard, and installation mode (ISO defaults to `native`).
6. Review storage layout; enable full-disk encryption if desired.
7. Export `AIONOS_ALLOW_INSTALL=1` in the console gate and confirm disk actions.
8. Choose a profile (user, professional, enterprise-vip) and review the summary.
9. Trigger the install and monitor `/var/log/aionos-installer.log` for progress.
10. Reboot into the installed system.

## Native Linux

1. Start from an Ubuntu 22.04 base with network access.
2. Install prerequisites: `sudo apt-get install -y git curl build-essential python3.11 python3.11-venv python3.11-dev` and install Node.js 18 LTS plus `pnpm` (`core/installer/bridge` relies on them).
3. Clone the repository and copy `.env` from `config/templates/.env.example`.
4. Run `pnpm install` in `core/installer/bridge` to prepare the privileged task server.
5. Launch the bridge with `AIONOS_ALLOW_INSTALL=1 pnpm start`.
6. In a second terminal, run `pnpm install && pnpm dev` inside `console` to start the wizard UI.
7. Connect to `https://localhost:3000/wizard` and select **Native Install**.
8. Pick your profile and network options.
9. Confirm disk operations only after reviewing the plan.
10. Reboot when prompted.

## Windows services without Docker

1. Install Git for Windows, Python 3.11, Node.js 18 LTS, PostgreSQL, Redis, and NSSM (`C:\\nssm\\nssm.exe` or export `NSSM_PATH`).
2. Clone the repository and inspect `config/templates/.env.example` for port/database overrides.
3. Run `pwsh ./scripts/install_win.ps1` from an elevated PowerShell prompt.
4. When prompted, provide database credentials or allow the script to create them (if PostgreSQL tools are present).
5. Wait for the script to build the console and gateway via `pnpm`, register the `Omerta*` services, and start them.
6. Confirm health at `http://localhost:3000` and tail service logs if troubleshooting is required.

## Docker (manual)

1. Ensure Docker Engine 24+ and Docker Compose V2 are installed.
2. Clone the repository and copy `.env` from `config/templates/.env.example`.
3. Set `AION_PROFILE` to `user`, `professional`, or `enterprise-vip` in `.env`.
4. Run `docker compose -f docker-compose.quickstart.yml up -d` (or substitute another compose file such as `docker-compose.yml` if you need the production baseline).
5. Access the wizard at `http://localhost:3000/wizard` to review status.
6. Confirm service health via the console dashboard.
7. Tear down with `docker compose down` when finished.

---

## نسخه فارسی

# شروع سریع

این راهنما هر استقرار پشتیبانی‌شده را در ده گام یا کمتر خلاصه می‌کند. مگر خلاف آن ذکر شده باشد، همه فرمان‌ها را به‌صورت root یا با `sudo` اجرا کنید.

## شروع سریع کانتینری

### لینوکس (Docker Engine)

1. Git، Docker Engine 24+ همراه با افزونه Compose و Python 3.11 یا جدیدتر را نصب کنید.
2. مخزن را کلون کنید: `git clone https://github.com/Hamedghz/OMERTAOS.git && cd OMERTAOS`.
3. بسته را اجرا کنید: `./install.sh --profile user` (در صورت نیاز `professional` یا `enterprise-vip`).
4. برای استفاده از [`docker-compose.local.yml`](../docker-compose.local.yml) در پروفایل سبک توسعه‌دهنده، `--local` را اضافه کنید.
5. زمانی که می‌خواهید اسکریپت پیش از راه‌اندازی سرویس‌ها تازه‌ترین کامیت‌ها را بگیرد، `--update` را استفاده کنید.
6. خروجی بررسی پیش‌نیاز و راه‌اندازی compose در [`scripts/quicksetup.sh`](../scripts/quicksetup.sh) را مشاهده کنید؛ اگر `.env` موجود نباشد به‌طور خودکار از [`config/templates/.env.example`](../config/templates/.env.example) ساخته می‌شود.
7. کنسول را در `http://localhost:3000` باز کنید و ویزارد راه‌اندازی را کامل کنید.
8. سلامت سرویس را از داشبورد بررسی کنید (کارت‌های `Control`، `Gateway`، `Console` باید سبز باشند).
9. در پایان، برای توقف استک `docker compose down` را اجرا کنید.

### ویندوز 11 / WSL2

1. Git برای ویندوز، Docker Desktop (با یکپارچه‌سازی WSL فعال) و PowerShell 7+ را نصب کنید.
2. مخزن را کلون کنید: `git clone https://github.com/Hamedghz/OMERTAOS.git`.
3. از یک PowerShell ارتقایافته در ریشه مخزن، `pwsh ./install.ps1 -Profile user` را اجرا کنید (یا `professional` / `enterprise-vip`).
4. برای لایه توسعه‌دهنده `-Local` یا برای گرفتن کامیت‌های تازه پیش از راه‌اندازی کانتینرها `-Update` را اضافه کنید.
5. این اسکریپت [`docker-compose.yml`](../docker-compose.yml) را از طریق [`scripts/quicksetup.ps1`](../scripts/quicksetup.ps1) اجرا می‌کند؛ خروجی را برای هشدار پیش‌نیازها بررسی کنید.
6. هنگام درخواست، در Docker Desktop وارد شوید تا پروژه compose بتواند شروع شود.
7. از ویندوز `http://localhost:3000` را باز کنید تا ویزارد را کامل کنید.
8. پس از پایان آزمایش با PowerShell دستور `docker compose down` را اجرا کنید.

## ISO / کیوسک

1. تازه‌ترین آرتیفکت انتشار را از مخزن انتشار دریافت کرده و checksum را بررسی کنید (به [`docs/release.md`](release.md) مراجعه کنید).
2. ISO را روی فلش بنویسید (`dd if=aionos.iso of=/dev/sdX bs=4M status=progress`).
3. سیستم هدف را در صورت پشتیبانی با Secure Boot بوت کنید.
4. پس از بالا آمدن کیوسک، اتصال شبکه را تأیید و **Start Installer** را بزنید.
5. زبان، صفحه‌کلید و حالت نصب را انتخاب کنید (پیش‌فرض ISO برابر `native` است).
6. چیدمان ذخیره‌سازی را مرور کنید؛ در صورت نیاز رمزگذاری کامل دیسک را فعال کنید.
7. متغیر `AIONOS_ALLOW_INSTALL=1` را در دروازه کنسول تنظیم و عملیات دیسک را تأیید کنید.
8. پروفایل (user، professional، enterprise-vip) را انتخاب و خلاصه را مرور کنید.
9. نصب را آغاز کنید و پیشرفت را در `/var/log/aionos-installer.log` دنبال کنید.
10. سیستم را ریبوت کنید.

## لینوکس بومی

1. از اوبونتو 22.04 با دسترسی شبکه شروع کنید.
2. پیش‌نیازها را نصب کنید: `sudo apt-get install -y git curl build-essential python3.11 python3.11-venv python3.11-dev` و Node.js 18 LTS همراه با `pnpm` را نصب کنید (`core/installer/bridge` به آن‌ها متکی است).
3. مخزن را کلون کرده و `.env` را از `config/templates/.env.example` کپی کنید.
4. در `core/installer/bridge` دستور `pnpm install` را اجرا کنید تا سرور وظیفه دارای امتیاز آماده شود.
5. پل را با `AIONOS_ALLOW_INSTALL=1 pnpm start` راه‌اندازی کنید.
6. در ترمینال دوم، داخل `console` دستور `pnpm install && pnpm dev` را اجرا کنید تا رابط ویزارد آغاز شود.
7. به `https://localhost:3000/wizard` متصل شوید و **Native Install** را انتخاب کنید.
8. پروفایل و گزینه‌های شبکه را برگزینید.
9. فقط پس از بررسی طرح، عملیات دیسک را تأیید کنید.
10. در صورت درخواست، ریبوت کنید.

## سرویس‌های ویندوز بدون Docker

1. Git برای ویندوز، Python 3.11، Node.js 18 LTS، PostgreSQL، Redis و NSSM (`C:\\nssm\\nssm.exe` یا متغیر `NSSM_PATH`) را نصب کنید.
2. مخزن را کلون کرده و برای تغییر پورت/دیتابیس `config/templates/.env.example` را بررسی کنید.
3. از PowerShell ارتقایافته `pwsh ./scripts/install_win.ps1` را اجرا کنید.
4. در صورت درخواست، اعتبارهای پایگاه‌داده را ارائه کنید یا اجازه دهید اسکریپت آن‌ها را بسازد (اگر ابزار PostgreSQL موجود باشد).
5. منتظر بمانید تا اسکریپت کنسول و دروازه را با `pnpm` بسازد، سرویس‌های `Omerta*` را ثبت و راه‌اندازی کند.
6. سلامت را در `http://localhost:3000` تأیید و در صورت نیاز لاگ سرویس‌ها را مشاهده کنید.

## Docker (دستی)

1. از نصب بودن Docker Engine 24+ و Docker Compose V2 مطمئن شوید.
2. مخزن را کلون کرده و `.env` را از `config/templates/.env.example` کپی کنید.
3. در `.env` مقدار `AION_PROFILE` را به `user`، `professional` یا `enterprise-vip` تنظیم کنید.
4. دستور `docker compose -f docker-compose.quickstart.yml up -d` را اجرا کنید (یا در صورت نیاز به خط پایه تولید، فایل دیگری مانند `docker-compose.yml` را جایگزین کنید).
5. برای بررسی وضعیت به `http://localhost:3000/wizard` دسترسی پیدا کنید.
6. سلامت سرویس‌ها را از داشبورد کنسول تأیید کنید.
7. در پایان با `docker compose down` استک را متوقف کنید.
