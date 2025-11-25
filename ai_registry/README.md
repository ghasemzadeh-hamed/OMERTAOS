# Agent-OS AI Registry

The AI Registry stores metadata for models, algorithms, and services that AION-OS resolves at runtime. It mirrors the contract described in [`docs/agentos_ai_registry.md`](../docs/agentos_ai_registry.md) and is consumed by the gateway, console, control plane, and installers.

## Layout

- `REGISTRY.yaml` – top-level catalog index read by automation and installers.
- `registry.lock.json` – integrity hashes for reproducible deployments.
- `models/`, `algorithms/`, `services/` – categorized manifests with fields such as `requiresApiKey`, `integrity`, and `auto_update`.
- `scripts/` – utilities for catalog maintenance and installation (`update_catalog.py`, `install_model.py`, `install_service.py`).
- `config/` – policy configuration for updates and installer defaults.
- `security/` – minisign public keys and integrity material.
- `.github/workflows/` – scheduled workflow that refreshes the registry (`update-registry.yml`).

## Usage

- Reference registry entries as `model://<name>` or `service://<name>` in configuration and agent recipes; the gateway resolves them using [`ai_registry/REGISTRY.yaml`](REGISTRY.yaml).
- Run `python ai_registry/scripts/update_catalog.py` to regenerate `registry.lock.json` and normalize manifests when metadata changes.
- For manual installs, use `python ai_registry/scripts/install_model.py --name <id>` or `install_service.py` to fetch artifacts declared in manifests.
- CI refresh is handled by `.github/workflows/update-registry.yml`, which runs `update_catalog.py` and commits lockfile changes.

---

## نسخه فارسی

# رجیستری هوش مصنوعی Agent-OS

رجیستری هوش مصنوعی فراداده مدل‌ها، الگوریتم‌ها و سرویس‌هایی را ذخیره می‌کند که AION-OS در زمان اجرا به آن‌ها رجوع می‌کند. این رجیستری قرارداد توضیح‌داده‌شده در [`docs/agentos_ai_registry.md`](../docs/agentos_ai_registry.md) را بازتاب می‌دهد و توسط دروازه، کنسول، صفحه کنترل و نصاب‌ها مصرف می‌شود.

## ساختار

- `REGISTRY.yaml` – شاخص کاتالوگ سطح بالا که توسط خودکارسازی و نصاب‌ها خوانده می‌شود.
- `registry.lock.json` – هش‌های یکپارچگی برای استقرارهای قابل تکرار.
- `models/`، `algorithms/`، `services/` – مانیفست‌های دسته‌بندی‌شده با فیلدهایی مانند `requiresApiKey`، `integrity` و `auto_update`.
- `scripts/` – ابزارهای نگهداری و نصب کاتالوگ (`update_catalog.py`، `install_model.py`، `install_service.py`).
- `config/` – پیکربندی سیاست برای به‌روزرسانی‌ها و پیش‌فرض‌های نصاب.
- `security/` – کلیدهای عمومی minisign و مواد یکپارچگی.
- `.github/workflows/` – گردش‌کار زمان‌بندی‌شده که رجیستری را تازه‌سازی می‌کند (`update-registry.yml`).

## نحوه استفاده

- ورودی‌های رجیستری را به‌صورت `model://<name>` یا `service://<name>` در پیکربندی و دستورالعمل‌های عامل ارجاع دهید؛ دروازه آن‌ها را با استفاده از [`ai_registry/REGISTRY.yaml`](REGISTRY.yaml) حل می‌کند.
- برای بازتولید `registry.lock.json` و همگام‌سازی مانیفست‌ها هنگام تغییر فراداده، `python ai_registry/scripts/update_catalog.py` را اجرا کنید.
- برای نصب دستی، از `python ai_registry/scripts/install_model.py --name <id>` یا `install_service.py` برای دریافت آرتیفکت‌های تعریف‌شده در مانیفست استفاده کنید.
- نوسازی CI توسط `.github/workflows/update-registry.yml` انجام می‌شود که `update_catalog.py` را اجرا کرده و تغییرات قفل را کامیت می‌کند.
