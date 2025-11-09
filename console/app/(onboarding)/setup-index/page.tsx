'use client';

import { ReactNode, useMemo, useState } from 'react';
import GlassPanel from '@/components/GlassPanel';

const steps = [
  'زبان و جهت نمایش',
  'اتصال پایگاه‌داده',
  'انتخاب مدل‌های هوش مصنوعی',
  'تأیید نهایی پیکربندی',
] as const;

type StepIndex = 0 | 1 | 2 | 3;

type StepContent = {
  title: string;
  description: string;
  body: ReactNode;
};

export default function SetupPage() {
  const [activeStep, setActiveStep] = useState<StepIndex>(0);
  const telemetryDefault = (process.env.NEXT_PUBLIC_TELEMETRY_OPT_IN ?? 'false').toLowerCase() === 'true';
  const [telemetryOptIn, setTelemetryOptIn] = useState<boolean>(telemetryDefault);

  const stepContent = useMemo<StepContent[]>(
    () => [
      {
        title: 'ترجیح زبان و جهت متن',
        description: 'انتخاب زبان پیش‌فرض رابط کاربری و تنظیم جهت نمایش برای تجربه کاملاً RTL.',
        body: (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">انتخاب زبان</span>
              <select className="glass-input cursor-pointer bg-white/10">
                <option value="fa">فارسی (پیشنهادی)</option>
                <option value="en">English</option>
              </select>
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">جهت رابط</span>
              <select className="glass-input cursor-pointer bg-white/10">
                <option value="rtl">RTL - راست به چپ</option>
                <option value="ltr">LTR - چپ به راست</option>
              </select>
            </label>
            <label className="space-y-2 text-right sm:col-span-2">
              <span className="text-sm text-white/75">تنظیمات پوسته</span>
              <div className="flex flex-wrap gap-3">
                {['Dark', 'Dim', 'Light'].map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    className="glass-button px-6"
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </label>
          </div>
        ),
      },
      {
        title: 'اتصال به پایگاه‌داده‌های عملیاتی',
        description: 'مسیرهای Postgres، Redis و MinIO را وارد کنید تا سرویس‌ها آمادهٔ همگام‌سازی شوند.',
        body: (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-right sm:col-span-2">
              <span className="text-sm text-white/75">نشانی Postgres (DSN)</span>
              <input className="glass-input" placeholder="postgresql://user:pass@localhost:5432/aion" />
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">آدرس Redis</span>
              <input className="glass-input" placeholder="redis://localhost:6379/0" />
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">MinIO Endpoint</span>
              <input className="glass-input" placeholder="http://localhost:9000" />
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">Bucket پیش‌فرض</span>
              <input className="glass-input" placeholder="aion-artifacts" />
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">کلید دسترسی MinIO</span>
              <input className="glass-input" placeholder="ACCESS_KEY" />
            </label>
            <label className="space-y-2 text-right">
              <span className="text-sm text-white/75">کلید مخفی MinIO</span>
              <input className="glass-input" placeholder="SECRET_KEY" type="password" />
            </label>
          </div>
        ),
      },
      {
        title: 'مسیر هوش مصنوعی و مدل‌ها',
        description: 'برای مسیریابی تطبیقی، مدل‌های محلی یا ابری و تنظیمات هزینه را مشخص کنید.',
        body: (
          <div className="space-y-4 text-right">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm text-white/75">ارائه‌دهنده پیش‌فرض</span>
                <select className="glass-input cursor-pointer bg-white/10">
                  <option>Ollama (محلی)</option>
                  <option>OpenAI</option>
                  <option>Google Gemini</option>
                </select>
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">مدل مکالمه</span>
                <input className="glass-input" placeholder="gpt-4o-mini" />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">مدل جستجوی برداری</span>
                <input className="glass-input" placeholder="nomic-embed-text" />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">سقف هزینه ماهانه (USD)</span>
                <input className="glass-input" type="number" placeholder="250" />
              </label>
            </div>
            <label className="space-y-2">
              <span className="text-sm text-white/75">سیاست بارگذاری دانش</span>
              <textarea className="glass-input h-28 resize-none" placeholder="قوانین بارگذاری را اینجا بنویسید" />
            </label>
          </div>
        ),
      },
      {
        title: 'مرور نهایی و شروع',
        description: 'تنظیمات را بررسی و برای راه‌اندازی سرویس‌های Control و Gateway تأیید کنید.',
        body: (
          <div className="space-y-4 text-right">
            <div className="rounded-2xl border border-white/15 bg-white/5 p-4">
              <h3 className="text-sm font-medium text-white/80">چک‌لیست آماده‌سازی</h3>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                <li>• اتصال پایگاه‌داده‌ها برقرار است</li>
                <li>• مدل‌های پیش‌فرض انتخاب شده‌اند</li>
                <li>• دسترسی کنسول ایمن‌سازی شده است</li>
              </ul>
            </div>
            <label className="flex items-center justify-between rounded-2xl border border-white/15 bg-white/5 px-4 py-3">
              <span className="text-sm text-white/75">ارسال تلمتری ناشناس (اختیاری)</span>
              <input
                type="checkbox"
                className="h-5 w-5 cursor-pointer accent-emerald-500"
                checked={telemetryOptIn}
                onChange={(event) => setTelemetryOptIn(event.target.checked)}
              />
            </label>
            <p className="text-xs leading-6 text-white/60">
              مقدار پیش‌فرض با متغیر محیطی <code className="rounded bg-white/10 px-1">AION_TELEMETRY_OPT_IN</code> کنترل می‌شود و تا زمانی که به طور صریح فعال نشود، هیچ داده‌ای ارسال نمی‌گردد.
            </p>
            <p className="text-sm leading-7 text-white/70">
              با تأیید، سرویس‌های AION-OS بر اساس تنظیمات وارد شده راه‌اندازی می‌شوند و داشبورد زنده می‌شود.
            </p>
          </div>
        ),
      },
    ],
    [telemetryOptIn],
  );

  const goToStep = (direction: 'prev' | 'next') => {
    setActiveStep((current) => {
      if (direction === 'prev') {
        return (Math.max(0, current - 1) as StepIndex);
      }
      return (Math.min(steps.length - 1, current + 1) as StepIndex);
    });
  };

  return (
    <main className="min-h-dvh p-6 text-white" dir="rtl">
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <GlassPanel className="p-4 sm:p-6">
          <header className="flex flex-col gap-2 text-right sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-white/90">جادوگر راه‌اندازی AION-OS</h1>
              <p className="text-sm text-white/65">پیکربندی سریع Control، Gateway و منابع داده با طراحی Liquid Glass</p>
            </div>
            <span className="text-sm text-white/60">گام {activeStep + 1} از {steps.length}</span>
          </header>
          <div className="mt-4 flex flex-wrap justify-end gap-2">
            {steps.map((label, index) => {
              const isActive = index === activeStep;
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => setActiveStep(index as StepIndex)}
                  className={`glass-button px-4 py-2 text-xs sm:text-sm ${isActive ? 'bg-white/25' : 'bg-white/10 hover:bg-white/15'}`}
                >
                  {index + 1}. {label}
                </button>
              );
            })}
          </div>
        </GlassPanel>

        <GlassPanel className="p-6 space-y-6">
          <div className="space-y-2 text-right">
            <h2 className="text-xl font-semibold text-white/90">{stepContent[activeStep].title}</h2>
            <p className="text-sm text-white/65">{stepContent[activeStep].description}</p>
          </div>
          <div>{stepContent[activeStep].body}</div>
          <div className="flex flex-wrap justify-between gap-3">
            <button
              type="button"
              onClick={() => goToStep('prev')}
              disabled={activeStep === 0}
              className="glass-button px-6 disabled:cursor-not-allowed disabled:opacity-40"
            >
              مرحله قبلی
            </button>
            <button
              type="button"
              onClick={() => goToStep('next')}
              disabled={activeStep === steps.length - 1}
              className="glass-button px-6 disabled:cursor-not-allowed disabled:opacity-40"
            >
              مرحله بعدی
            </button>
          </div>
        </GlassPanel>

        <GlassPanel className="p-5 text-right">
          <h3 className="text-base font-medium text-white/85">راهنمای دسترسی و عملکرد</h3>
          <p className="mt-2 text-sm leading-7 text-white/65">
            افکت‌های Liquid Glass با backdrop-filter و گرادیان‌های نرم ایجاد شده‌اند تا خوانایی حفظ شود. برای عملکرد بهتر، blur محدود
            به 16px و روشنایی کنترل شده است؛ در مرورگرهایی که از این ویژگی پشتیبانی نمی‌کنند، پس‌زمینه مات جایگزین می‌شود.
          </p>
        </GlassPanel>
      </div>
    </main>
  );
}
