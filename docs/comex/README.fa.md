# برنامه آمادگی ۱۰روزه OMERTAOS برای COMEX

**نقش سند:** برنامه اجرایی و معیار پذیرش نمایش فنی. این سند به‌تنهایی Evidence محسوب نمی‌شود.

## هدف

OMERTAOS باید به‌عنوان یک **نمونه پژوهشی قابل دفاع و قابل نمایش برای حامی و سرمایه‌گذار** ارائه شود. هدف این برنامه، اثبات یک مسیر محدود اما واقعی است؛ نه ادعای آماده‌بودن برای Production.

مسیر مرجع سیستم:

`Console -> Gateway -> Control -> Runtime Daemon`

قرارداد دموی اصلی:

`Operator -> Agent Action -> Gateway Admission -> Control Policy -> Runtime Execution -> Audit Evidence`

دمو باید دو حالت را به‌شکل تکرارپذیر نشان دهد:

1. یک عملیات مجاز تا Runtime پیش می‌رود و Evidence قابل مشاهده تولید می‌کند.
2. همان مسیر برای یک Capability غیرمجاز رد می‌شود و علت رد در Audit ثبت می‌شود.

## مدل Evidence

| سطح | تعریف | عبارت مجاز در ارائه |
|---|---|---|
| **E1 - Repository Verified** | ادعا با تست اجرایی یا Gate قطعی ریپو بررسی می‌شود. | Verified in repository |
| **E2 - Implemented Prototype** | کد و تست هدفمند وجود دارد، اما پذیرش کامل سیستم انجام نشده است. | Implemented prototype |
| **E3 - Design Target** | طراحی مشخص است، ولی پیاده‌سازی یا اعتبارسنجی کامل نیست. | Design target / roadmap |
| **E0 - Unsupported** | Evidence کافی وجود ندارد. | به‌عنوان قابلیت فعلی بیان نشود |

هر ادعای ارائه باید به Commit، فرمان تست، نتیجه و محدودیت آن متصل باشد. مرجع عمومی ادعاها در [Evidence and claims](../research/evidence-and-claims.md) نگهداری می‌شود.

## برنامه ۱۰روزه

| روز | تمرکز | خروجی اجباری | Gate خروج |
|---|---|---|---|
| ۱ | Freeze، Baseline و Demo Contract | Commit مبنا، فهرست سرویس‌ها، قرارداد دموی اصلی و Backlog منجمد | محدوده دمو و موارد خارج از محدوده تأیید شده باشد |
| ۲ | Quickstart واقعی | نصب و Setup تکرارپذیر، ثبت کاربر/رمز، Health و Login | اجرای تمیز بدون SQL یا اصلاح دستی |
| ۳ | E2E چهار سرویس | عبور یک Task واقعی از Console تا Runtime و بازگشت نتیجه | Trace و Evidence برای کل مسیر موجود باشد |
| ۴ | Policy Allow/Deny و Audit | سناریوی مجاز، سناریوی ردشده و Audit قابل ارائه | نتیجه و علت Policy در UI و لاگ قابل مشاهده باشد |
| ۵ | پذیرش Native Linux | نصب، Start/Stop/Restart، Health و Rollback روی میزبان هدف | گزارش Acceptance با محیط دقیق ثبت شود |
| ۶ | Reliability و Offline Demo | Recovery، Timeout، داده نمایشی محلی و Runbook آفلاین | دمو بدون اینترنت و پس از Restart قابل تکرار باشد |
| ۷ | UI نمایشگاهی و Observability | مسیرهای ضروری Console، وضعیت واقعی سرویس‌ها و حذف داده ساختگی | هیچ کنترل اصلی بی‌عمل و هیچ KPI جعلی باقی نماند |
| ۸ | بسته Sponsor/Investor | Pitch، معماری، Evidence، Funding Ask و Roadmap دوازده‌ماهه | هر ادعا سطح Evidence و مرز روشن داشته باشد |
| ۹ | تمرین Red-team | اجرای سناریوی خرابی، سؤال سخت، Backup laptop و زمان‌بندی دمو | سه اجرای متوالی در زمان هدف موفق باشد |
| ۱۰ | Freeze و Exhibition Release | Tag/Commit نهایی، Artifactها، Checksums، Runbook و Go/No-Go | Scorecard حداقل ۸۵ از ۱۰۰ و Blocker بحرانی صفر باشد |

## محدوده اجرا

### Must

- Quickstart واقعی و تکرارپذیر؛
- Login و Setup بدون دست‌کاری دستی دیتابیس؛
- یک مسیر E2E واقعی و یک Policy Deny واقعی؛
- Audit Evidence قابل مشاهده؛
- Health واقعی سرویس‌ها؛
- Runbook دمو، Recovery و حالت آفلاین؛
- بسته فنی/سرمایه‌گذاری با ادعاهای درجه‌بندی‌شده.

### Nice to have

- UI جزئیات Trace؛
- Export گزارش Audit؛
- چند Profile آماده برای دموی محلی؛
- نمودار ساده وضعیت و زمان پاسخ با منبع واقعی.

### خارج از محدوده این Sprint

- بازنویسی معماری؛
- ادعای Production-ready یا امنیت کامل؛
- Distributed consensus، Federation یا مقیاس‌پذیری اثبات‌نشده؛
- Benchmark رقابتی بدون پروتکل و داده کنترل‌شده؛
- اضافه‌کردن قابلیت نمایشی بدون backend واقعی.

## Definition of Done

برنامه زمانی Done است که همه موارد زیر برقرار باشند:

- Quickstart روی محیط ثبت‌شده از صفر اجرا شود؛
- کاربر Setup در دیتابیس ثبت و با همان رمز Login کند؛
- مسیر مرجع چهار سرویس با Task واقعی اثبات شود؛
- Allow و Deny همراه Audit Evidence نمایش داده شوند؛
- همه کنترل‌های مسیر دموی Console کار کنند یا صریحاً Unavailable باشند؛
- هیچ KPI، پروژه، پیام یا نتیجه ساختگی به‌عنوان داده واقعی نمایش داده نشود؛
- تست‌ها، نسخه ابزارها، Commit و محدودیت‌ها ثبت شوند؛
- Runbook آفلاین، Recovery و نسخه پشتیبان دمو آماده باشد؛
- Scorecard نهایی حداقل ۸۵/۱۰۰ و Go/No-Go ثبت شود.

## Scorecard

| حوزه | امتیاز |
|---|---:|
| Quickstart و تکرارپذیری | ۲۰ |
| E2E و Policy/Audit | ۲۵ |
| Reliability و Recovery | ۱۵ |
| Console و Observability | ۱۵ |
| Evidence و صداقت ادعاها | ۱۵ |
| Pitch، Runbook و آمادگی نمایش | ۱۰ |
| **جمع** | **۱۰۰** |

## قواعد به‌روزرسانی

- وضعیت واقعی در [دفتر پیشرفت و Evidence](progress.fa.md) ثبت می‌شود.
- هر ردیف پیشرفت باید تاریخ، Commit، فرمان اعتبارسنجی، نتیجه و محدودیت داشته باشد.
- «کد وجود دارد» معادل «E2E پاس شده» نیست.
- گزارش تاریخی بدون اجرای مجدد، وضعیت فعلی محسوب نمی‌شود.
- تغییر وضعیت به Done فقط بعد از عبور Gate همان روز مجاز است.
