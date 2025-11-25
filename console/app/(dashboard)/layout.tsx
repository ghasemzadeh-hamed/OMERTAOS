import { ReactNode } from 'react';
import { redirect } from 'next/navigation';
import GlassPanel from '@/components/GlassPanel';
import NavTabs from '@/components/NavTabs';
import UserMenu from '@/components/UserMenu';
import { safeGetServerSession } from '@/lib/session';

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const session = await safeGetServerSession();

  if (!session) {
    redirect('/login');
  }

  const role = (session.user as any)?.role ?? 'USER';

  return (
    <section className="min-h-dvh text-white" dir="rtl">
      <div className="min-h-dvh grid gap-4 px-4 py-6 lg:grid-cols-[280px_1fr] lg:grid-rows-[auto_1fr]">
        <header className="lg:col-span-2">
          <GlassPanel className="flex flex-wrap items-center justify-between gap-4 p-4">
            <div className="space-y-1 text-right">
              <h1 className="text-2xl font-semibold text-white/90">داشبُرد AION-OS</h1>
              <p className="text-sm text-white/65">پایش بلادرنگ عامل‌ها، جریان‌ها و سیاست‌ها در یک فضای شیشه‌ای</p>
            </div>
            <UserMenu email={session.user?.email} role={role} />
          </GlassPanel>
        </header>

        <aside className="hidden min-h-0 lg:flex lg:flex-col">
          <GlassPanel className="flex flex-1 flex-col gap-4 p-4 text-right">
            <div>
              <h2 className="text-lg font-semibold text-white/85">وضعیت سرویس‌ها</h2>
              <p className="mt-1 text-sm text-white/60">Redis • Postgres • Qdrant • MinIO</p>
            </div>
            <div className="space-y-3 text-sm text-white/70">
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <span className="font-medium text-white/80">کنترل</span>
                <p className="mt-1 leading-6">API و gRPC در حال اجرا هستند؛ آخرین بررسی سلامت 2 دقیقه پیش.</p>
              </div>
              <div className="rounded-xl border border-white/10 bg-white/5 p-3">
                <span className="font-medium text-white/80">Gateway</span>
                <p className="mt-1 leading-6">مسیرهای گفتگو و رویداد فعال هستند؛ 3 وظیفه در صف.</p>
              </div>
            </div>
            <div className="mt-auto text-sm text-white/60">
              Liquid Glass: طراحی مبتنی بر blur و highlight برای خوانایی بهتر در دارک‌مود.
            </div>
          </GlassPanel>
        </aside>

        <main className="flex min-h-0 flex-col gap-4">
          <GlassPanel className="p-4">
            <NavTabs role={role} />
          </GlassPanel>
          <div className="grid gap-4 lg:grid-cols-2">
            <GlassPanel className="p-4 text-right">
              <h2 className="text-lg font-semibold text-white/85">سلامت عامل‌ها</h2>
              <p className="mt-2 text-sm leading-6 text-white/70">تمام عامل‌های عملیاتی در وضعیت پایدار هستند. 12 سناریو فعال.</p>
            </GlassPanel>
            <GlassPanel className="p-4 text-right">
              <h2 className="text-lg font-semibold text-white/85">مصرف مدل</h2>
              <p className="mt-2 text-sm leading-6 text-white/70">میانگین تأخیر 860ms و هزینه ماهانه برآوردی 178 دلار.</p>
            </GlassPanel>
          </div>
          <GlassPanel className="p-4 text-right">
            {children}
          </GlassPanel>
        </main>
      </div>
    </section>
  );
}
