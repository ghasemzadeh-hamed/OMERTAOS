# دفتر پیشرفت و Evidence برنامه COMEX

**نقش سند:** گزارش جاری و قابل ممیزی.
**آخرین به‌روزرسانی:** ۲۰۲۶-۰۸-۲۱
**شاخه:** `codex/capo-r4-validation`

## خلاصه وضعیت

| روز | وضعیت | سطح فعلی | Evidence موجود | مانع خروج |
|---|---|---|---|---|
| ۱ - Baseline و Demo Contract | در حال انجام | E2 | قرارداد دمو و مدل Evidence مستند شده؛ معماری مرجع تست دارد | Freeze نهایی و فهرست Artifactها ثبت نشده است |
| ۲ - Quickstart | در حال اعتبارسنجی | E2 | Setup، ثبت Admin، Login، Compose و Health روی همین میزبان تست شده‌اند | اجرای مجدد از محیط کاملاً تمیز باید ثبت شود |
| ۳ - E2E چهار سرویس | در حال انجام | E2 | Console از Gateway boundary برای Task استفاده می‌کند؛ Gateway و Control/Runtime موجودند | یک Task موفق با Trace کامل چهار سرویس هنوز ثبت نشده است |
| ۴ - Policy و Audit | در حال انجام | E2 | Config Center واقعی با چرخه Propose/Apply/Revert، ذخیره Postgres و Audit اضافه و تست شده است | سناریوی Policy Allow/Deny نمایشگاهی و Evidence یکپارچه هنوز لازم است |
| ۵ - Native Linux | شروع نشده | E3 | راهنمای Native و گزارش CAPO موجود است | Acceptance واقعی روی میزبان هدف لازم است |
| ۶ - Reliability/Offline | شروع نشده | E3 | برخی Health و Recovery pathها وجود دارند | Runbook آفلاین و تست Restart/Timeout لازم است |
| ۷ - Console/Observability | در حال اعتبارسنجی | E2 | ۳۶ مسیر ممیزی شده، منوی اصلی فعال، Health واقعی، Config/Network/Models/Run متصل و داده‌های ساختگی حذف شده‌اند | پوشش موبایل و E2E قابلیت‌های backend که اکنون صریحاً Unavailable هستند لازم است |
| ۸ - Sponsor package | در حال انجام | E3 | Research package، Evidence taxonomy و این برنامه موجود است | Pitch، Funding Ask و Roadmap نهایی باید یکپارچه شوند |
| ۹ - Red-team rehearsal | شروع نشده | E3 | معیار تمرین تعریف شده است | سه اجرای متوالی و سناریوهای خرابی ثبت نشده‌اند |
| ۱۰ - Exhibition release | شروع نشده | E3 | Gate نهایی تعریف شده است | Freeze، Artifact، Checksum، Scorecard و Go/No-Go لازم است |

## تغییرات ثبت‌شده

| تاریخ | Commit | تغییر | اعتبارسنجی |
|---|---|---|---|
| ۲۰۲۶-۰۸-۲۱ | `bea738d` | رفع Loop در Quickstart؛ ثبت Admin و Password hash و تکمیل Setup | تست واحد Setup، بررسی DB و Login مرورگر |
| ۲۰۲۶-۰۸-۲۱ | `1d8f4aa` | تکمیل ناوبری Console، فهرست قابلیت‌ها، Health منبع‌دار و حذف KPIهای ساختگی | Build کنسول، ممیزی ۲۹ مسیر و تست کنترل‌های اصلی مرورگر |
| ۲۰۲۶-۰۸-۲۱ | `e1f532e` | اتصال Chat/Agent به Task API از مسیر Gateway و احراز هویت داخلی server-only | ۱۵ تست Console، ۸ تست Gateway، Build Docker و Smoke test مرورگر |
| ۲۰۲۶-۰۸-۲۱ | `1c176f5` | تکمیل صفحات منبع‌دار، Config پایدار، Network/Models/Run، گارد API، Health و مسیرهای سازگاری | ۱۹ تست Console، ۵۰ تست Control، Build production و Docker، ممیزی مرورگر و تست 401/409 |

## Evidence اجرایی جاری

| بخش | فرمان یا مشاهده | نتیجه | مرز نتیجه |
|---|---|---|---|
| Console unit | `npm run test --prefix console -- --config vitest.config.mts` | Pass: ۹ فایل، ۱۹ تست | رفتار Runtime و E2E را اثبات نمی‌کند |
| Control unit/integration | `python -m pytest tests/control -q` | Pass: ۵۰ تست | پذیرش Native و Runtime موفق را اثبات نمی‌کند |
| Gateway unit | اجرای Vitest با Node 22 در Docker | Pass: ۳ فایل، ۸ تست | Host فعلی Node 18 با Vitest جدید سازگار نیست |
| Gateway build | `npm run build --prefix gateway` | Pass | اجرای کامل Compose را اثبات نمی‌کند |
| Console production build | Build مرحله Next.js در image | Pass | تعامل مرورگر را به‌تنهایی اثبات نمی‌کند |
| Console route audit | بازکردن ۳۶ مسیر محافظت‌شده و Smoke نهایی مسیرهای تغییرکرده | بدون 404 یا خطای صفحه؛ مسیر فارسی پس از رفع ناسازگاری i18n به Console هدایت شد | backend برخی قابلیت‌ها عمداً Unavailable است |
| Primary controls | ۸ لینک Sidebar، Choose Project، Theme، Config Save/Apply/Revert و Network validation | Pass | قابلیت‌های فاقد API عملیات ساختگی ندارند |
| API authorization | درخواست بدون Cookie به Config، Network و Models؛ تلاش تکرار Setup | `401` برای API محافظت‌شده و `409` برای Setup تکمیل‌شده | تست نقش‌های چندکاربره هنوز لازم است |
| Docker quickstart | Build و recreate سرویس‌های Console/Control؛ بررسی Compose Health | Console، Gateway، Control، Runtime، Postgres و Redis healthy | نصب کاملاً تمیز هنوز ثبت نشده است |
| Chat/Agent Task | ارسال درخواست read-only و بازکردن Run از UI | Task ID و صفحه Run واقعی ایجاد شد؛ Runtime و ذخیره وضعیت ناقص صریحاً خطا دادند و موفقیت ساختگی گزارش نشد | مسیر تا Control اثبات شد؛ اجرای موفق Runtime هنوز اثبات نشده است |
| Database | خواندن `SystemState` و `User` | `setup_completed=true` و `admin@local` با نقش `ADMIN` | فقط همین Compose volume را اثبات می‌کند |
| Fake data scan | جست‌وجوی KPIها و محتوای نمونه شناخته‌شده | مورد باقی‌مانده پیدا نشد | داده ساختگی جدید باید در Review کنترل شود |

## قابلیت‌های صادقانه محدودشده

صفحات مربوط به Agent catalog، Tenancy، Tool discovery، Update، Backup و برخی ابزارهای مدیریتی ممکن است UI داشته باشند، اما تا زمان وجود API واقعی و تست E2E به‌عنوان قابلیت کامل معرفی نمی‌شوند. Console باید در این حالت پیام `Unavailable` منبع‌دار نشان دهد و عملیات ساختگی تولید نکند.

ادعاهای زیر همچنان E0 هستند و نباید در ارائه به‌عنوان نتیجه فعلی بیان شوند:

- Production readiness؛
- ایزولیشن کامل Linux؛
- مقیاس‌پذیری یا Latency برتر؛
- Federation و Distributed consensus عملیاتی؛
- Security certification یا Penetration test مستقل.

## کارهای بعدی با اولویت

1. ثبت یک Task موفق با Trace کامل `Console -> Gateway -> Control -> Runtime`.
2. ساخت و تست سناریوی Policy Allow/Deny همراه Audit Evidence.
3. اجرای Quickstart از محیط تمیز و ثبت زمان، نسخه‌ها و Exit codeها.
4. تهیه Runbook Offline/Recovery و اجرای تست Restart/Timeout.
5. تکمیل Pitch، Funding Ask، Roadmap دوازده‌ماهه و Scorecard نهایی.

## قالب ثبت پیشرفت بعدی

| تاریخ | روز/هدف | Commit | فرمان/سناریو | نتیجه | Evidence level | محدودیت/اقدام بعدی |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | Dn | SHA | command or scenario | Pass/Fail | E0-E3 | concise boundary |
