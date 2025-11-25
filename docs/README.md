# AION-OS Documentation Hub

This directory provides enterprise-ready runbooks covering installation, configuration, and operations across every deployment mode.

## Quick start

See [`quickstart.md`](quickstart.md) for a ten-step launch path across ISO, native Linux, WSL, and Docker modes.

## Installation guides

Mode-specific instructions live under [`install/`](install):

- [`install/iso.md`](install/iso.md) — build and boot the kiosk ISO, including offline cache support.
- [`install/native.md`](install/native.md) — run the installer bridge on an existing Ubuntu host.
- [`install/wsl.md`](install/wsl.md) — bring the stack to Windows via WSL without touching disks.
- [`install/docker.md`](install/docker.md) — compose services for local or CI-driven clusters.

## Profiles and automation

Profile behaviour, feature toggles, and service enablement are described in [`profiles/`](profiles):

- [`profiles/user.md`](profiles/user.md)
- [`profiles/pro.md`](profiles/pro.md)
- [`profiles/enterprise.md`](profiles/enterprise.md)

The installer schema lives in `core/installer/profile/schemas.ts`, and default YAML manifests sit in `core/installer/profile/defaults/`.

## Security and compliance

Baseline hardening, update cadence, and secure boot guidance are documented in [`security/`](security):

- [`security/baseline.md`](security/baseline.md)
- [`security/updates.md`](security/updates.md)
- [`security/secure-boot-fde.md`](security/secure-boot-fde.md)

## Hardware compatibility

GPU, NIC, Wi‑Fi, and firmware matrices live in [`hcl/`](hcl). Use [`hcl/index.md`](hcl/index.md) as the entry point, with detail pages for GPUs (`hcl/gpu.md`) and networking (`hcl/nic.md`).

## Operations

- [`troubleshooting.md`](troubleshooting.md) — fixes for common install and runtime issues.
- [`release.md`](release.md) — SBOM, signing, and release validation process.
- [`privacy.md`](privacy.md) — optional telemetry and data handling.
- [`user_team_documentation.md`](user_team_documentation.md) — end-to-end user, admin, and installation guidance with FAQs and glossary.
- [`enterprise_it_infrastructure.md`](enterprise_it_infrastructure.md) — asset inventory, network segmentation, SOPs, DR, IAM, and recovery priorities for enterprise deployments.
- [`full_system_review.md`](full_system_review.md) — architecture, API, install, runbook, security, observability, and DR overview.

---

## نسخه فارسی

# مرکز مستندات AION-OS

این پوشه راهبردهای عملیاتی آماده برای سازمان‌ها را در بر می‌گیرد که نصب، پیکربندی و عملیات را در همه حالت‌های استقرار پوشش می‌دهد.

## شروع سریع

برای مسیر ده‌مرحله‌ای راه‌اندازی در حالت‌های ISO، لینوکس بومی، WSL و Docker به [`quickstart.md`](quickstart.md) مراجعه کنید.

## راهنماهای نصب

دستورالعمل‌های ویژه هر حالت در [`install/`](install) قرار دارند:

- [`install/iso.md`](install/iso.md) — ساخت و بوت ISO کیوسک، شامل پشتیبانی کش آفلاین.
- [`install/native.md`](install/native.md) — اجرای پل نصاب روی میزبان اوبونتوی موجود.
- [`install/wsl.md`](install/wsl.md) — آوردن استک به ویندوز از طریق WSL بدون دستکاری دیسک.
- [`install/docker.md`](install/docker.md) — سرهم‌بندی سرویس‌ها برای خوشه‌های محلی یا CI.

## پروفایل‌ها و خودکارسازی

رفتار پروفایل، سوییچ‌های ویژگی و فعال‌سازی سرویس در [`profiles/`](profiles) توضیح داده شده است:

- [`profiles/user.md`](profiles/user.md)
- [`profiles/pro.md`](profiles/pro.md)
- [`profiles/enterprise.md`](profiles/enterprise.md)

طرحواره نصاب در `core/installer/profile/schemas.ts` قرار دارد و مانیفست‌های پیش‌فرض YAML در `core/installer/profile/defaults/` هستند.

## امنیت و انطباق

سخت‌سازی پایه، برنامه به‌روزرسانی و راهنمایی Secure Boot در [`security/`](security) مستند شده‌اند:

- [`security/baseline.md`](security/baseline.md)
- [`security/updates.md`](security/updates.md)
- [`security/secure-boot-fde.md`](security/secure-boot-fde.md)

## سازگاری سخت‌افزاری

ماتریس‌های GPU، NIC، وای‌فای و میان‌افزار در [`hcl/`](hcl) قرار دارند. از [`hcl/index.md`](hcl/index.md) به‌عنوان نقطه ورود استفاده کنید و صفحات جزئیات GPU (`hcl/gpu.md`) و شبکه (`hcl/nic.md`) را ببینید.

## عملیات

- [`troubleshooting.md`](troubleshooting.md) — راه‌حل مشکلات رایج نصب و زمان اجرا.
- [`release.md`](release.md) — فرآیند SBOM، امضا و اعتبارسنجی انتشار.
- [`privacy.md`](privacy.md) — تلماتری اختیاری و مدیریت داده.
- [`user_team_documentation.md`](user_team_documentation.md) — راهنمای جامع کاربر، مدیر و نصب همراه با FAQ و واژه‌نامه.
- [`enterprise_it_infrastructure.md`](enterprise_it_infrastructure.md) — فهرست دارایی، تفکیک شبکه، SOP، DR، IAM و اولویت‌های بازیابی برای استقرارهای سازمانی.
- [`full_system_review.md`](full_system_review.md) — مرور معماری، API، نصب، راهنما، امنیت، مشاهده‌پذیری و DR.
