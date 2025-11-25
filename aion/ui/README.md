# AION Catalog UI

This directory holds the planned Next.js implementation of the catalog surfaces (Grid, ToolView, Editor, Chat Assistant). The frontend code is not present here, but the backend APIs, configuration, and worker synchronization layers that serve the UI are ready.

Key integrations:

- Catalog APIs live in [`aion/control/catalog_api.py`](../control/catalog_api.py) and surface agent and tool metadata to the console.
- Catalog sync workers run from [`aion/worker/catalog_sync.py`](../worker/catalog_sync.py) to keep the database aligned with registry and recipe files.
- UI wiring in [`aion/config/aion.yaml`](../config/aion.yaml) and [`aion/docker/compose.catalog.yml`](../docker/compose.catalog.yml) exposes the catalog services over HTTP when the compose profile is enabled.

When adding the React/Next.js code, point API calls to the gateway or control endpoints described above so the UI stays aligned with the existing catalog and worker logic.

---

## نسخه فارسی

# رابط کاربری کاتالوگ آیون

این پوشه محل پیاده‌سازی برنامه‌ریزی‌شده Next.js برای سطوح کاتالوگ (Grid، ToolView، Editor، Chat Assistant) است. کد فرانت‌اند در این مخزن موجود نیست، اما APIهای بک‌اند، پیکربندی و لایه‌های همگام‌سازی کارگر که رابط را تغذیه می‌کنند آماده‌اند.

یکپارچه‌سازی‌های کلیدی:

- APIهای کاتالوگ در [`aion/control/catalog_api.py`](../control/catalog_api.py) قرار دارند و فراداده عامل و ابزار را به کنسول ارائه می‌کنند.
- کارگران همگام‌سازی کاتالوگ از [`aion/worker/catalog_sync.py`](../worker/catalog_sync.py) اجرا می‌شوند تا پایگاه‌داده را با رجیستری و فایل‌های دستورالعمل همسو نگه دارند.
- سیم‌کشی رابط در [`aion/config/aion.yaml`](../config/aion.yaml) و [`aion/docker/compose.catalog.yml`](../docker/compose.catalog.yml) هنگام فعال شدن پروفایل compose سرویس‌های کاتالوگ را از طریق HTTP در معرض قرار می‌دهد.

هنگام افزودن کد React/Next.js، فراخوانی‌های API را به دروازه یا نقاط پایانی کنترل یادشده هدایت کنید تا رابط کاربری با منطق فعلی کاتالوگ و کارگر هماهنگ بماند.
