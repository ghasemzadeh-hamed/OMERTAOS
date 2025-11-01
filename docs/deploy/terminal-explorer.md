# اکسپلورر متنی و چت‌بات کانفیگ (Headless)

این راهنما سه گزینهٔ عملی برای راه‌اندازی «اکسپلورر + چت‌بات کانفیگ» در محیط‌های کاملاً ترمینالی ارائه می‌کند. هر گزینه بدون وابستگی به مرورگر گرافیکی کار می‌کند و مستقیماً به API کنترل (`aion-control`) متصل می‌شود.

> **پیش‌نیاز مشترک:** دسترسی HTTP به کنترل و یک توکن معتبر (`AION_TOKEN`).

---

## گزینه A) برنامهٔ Textual (پیشنهادی)

یک رابط متنی (TUI) بومی مبتنی بر [Textual](https://textual.textualize.io/) که پنل اکسپلورر (Providers/Modules/Data Sources) و چت‌بات فرمانی را کنار هم نمایش می‌دهد.

### نصب

```bash
python3 -m pip install --upgrade textual rich requests
```

### اجرا

```bash
python3 -m console.tui.explorer --api http://127.0.0.1:8001 --token "$AION_TOKEN"
```

### قابلیت‌ها

- فرمان‌های چت‌محور (`add provider …`, `set router …`, `add ds …`, `list providers` و ...)
- به‌روزرسانی بلادرنگ پانل Explorer با فشار `Ctrl+R`
- `Ctrl+D` برای نمایش راهنمای فرمان‌ها
- لاگ دستورها و پاسخ‌ها در سمت راست ترمینال

> اگر با SSH به سرور متصل هستید فقط کافی‌ست کتابخانه‌های بالا را روی همان سرور نصب کنید.

---

## گزینه B) وب‌سرور داخلی + مرورگر متنی (w3m/lynx)

اسکریپت [`scripts/aion-explorer`](../../scripts/aion-explorer) یک وب‌سرور محلی مینیمال (FastAPI + فرم HTML ساده) اجرا می‌کند و سپس نخستین مرورگر متنی موجود (`w3m`، `lynx` یا `links`) را روی همان ترمینال باز می‌کند.

### پیش‌نیاز

```bash
sudo apt-get install -y w3m # یا lynx/links
python3 -m pip install --upgrade fastapi uvicorn requests
```

### اجرا

```bash
AION_API=http://127.0.0.1:8001 \
AION_TOKEN="$AION_TOKEN" \
AION_EXPLORER_PORT=3030 \
scripts/aion-explorer
```

اسکریپت سرور را در پس‌زمینه اجرا کرده و مرورگر متنی را به آدرس `http://127.0.0.1:3030/` هدایت می‌کند. فرمان‌ها از طریق یک فرم ساده ارسال شده و پاسخ‌ها در همان صفحه لاگ می‌شوند.

### گزینه‌های قابل تنظیم

- `AION_EXPLORER_PORT`: پورت سرویس (پیش‌فرض 3030)
- `AION_EXPLORER_HOST`: آدرس گوش دادن (پیش‌فرض 127.0.0.1)
- `AION_EXPLORER_LOG`: مسیر لاگ خروجی سرور

برای خروج کافی‌ست کلید `q` را در w3m/lynx فشار دهید؛ اسکریپت سرور پس‌زمینه را متوقف می‌کند.

---

## گزینه C) حالت کیوسک برای محیط‌های دسکتاپ

در صورتی که روی یک میزکار یا VM با محیط گرافیکی کار می‌کنید، می‌توانید از همان سرور متنی استفاده کنید اما به‌جای مرورگر متنی، حالت «App Mode» کرومیوم/فایرفاکس را باز کنید:

```bash
AION_TOKEN="$AION_TOKEN" \
AION_EXPLORER_PORT=3030 \
AION_EXPLORER_LOG=/tmp/aion-explorer.log \
AION_EXPLORER_HOST=127.0.0.1 \
scripts/aion-explorer &

chromium --app="http://127.0.0.1:3030/?token=$AION_TOKEN" --kiosk
```

یا اگر می‌خواهید صرفاً مرورگر را جداگانه باز کنید:

```bash
python3 -m console.tui.web_server --api http://127.0.0.1:8001 --token "$AION_TOKEN"
# سپس روی همان سیستم: xdg-open http://127.0.0.1:3030/
```

مزیت این حالت اجرای یک UI تمام‌صفحه بدون نوار ابزار است؛ مناسب برای کیوسک یا اتاق عملیات.

---

## فرمان‌های پشتیبانی‌شده توسط چت‌بات

چه از TUI (گزینه A) استفاده کنید، چه از سرور وب (گزینه B/C)، همان موتور فرمانی در ماژول [`console/tui/api.py`](../../console/tui/api.py) فراخوانی می‌شود. فرمان‌های اصلی:

```
help
list providers|modules|datasources
add provider <name> key=... [kind=local|api] [base_url=...]
add ds <name> kind=postgres dsn=postgres://... [readonly=true]
set router policy=<default|auto> [budget=200] [failover=on|off]
reload router
test ds <name>
```

تمام خطاهای دریافتی از API کنترل با پیام‌های `❌` نمایش داده می‌شود تا در یک نگاه مشخص شود چه چیزی باید اصلاح شود.

---

## ادغام در جریان‌های CI/CD

- از آنجا که رابط‌ها کاملاً متنی هستند، می‌توان آن‌ها را در کانتینرهای CI نیز اجرا کرد (نمونه: `textual run ...` یا `scripts/aion-explorer`).
- برای تولید گزارش، خروجی تاریخچه را می‌توان از فایل لاگ (`AION_EXPLORER_LOG`) استخراج کرد.
- فرمان‌ها idempotent طراحی شده‌اند؛ چند بار ارسال شدن یک فرمان همان پاسخ قبلی را باز می‌گرداند مگر این‌که وضعیت کنترل تغییر کرده باشد.

---

### رفع اشکال معمول

| وضعیت | توضیح | راهکار |
| --- | --- | --- |
| `❌ خطا از API: 401` | توکن نامعتبر یا منقضی شده | مقدار `AION_TOKEN` را بررسی کنید. |
| `مرورگر متنی یافت نشد` | w3m/lynx نصب نیست | با `apt-get install w3m` نصب کنید یا از گزینه A استفاده کنید. |
| UI در SSH تاریک است | ترمینال بدون UTF-8 | متغیر `LC_ALL`/`LANG` را روی `en_US.UTF-8` یا `fa_IR.UTF-8` بگذارید. |

---

### ادامهٔ مسیر

- برای ترکیب این رابط‌ها با سناریوی استقرار Headless، راهنمای [استقرار Headless](./headless-cli.md) را دنبال کنید و سپس با یکی از گزینه‌های بالا کانفیگ را به صورت تعاملی انجام دهید.
- در صورت نیاز به توسعهٔ بیش‌تر رابط، می‌توانید کلاس‌های `ControlAPI` و `CommandProcessor` را گسترش دهید تا فرمان‌های سفارشی دیگری به TUI اضافه شود.
