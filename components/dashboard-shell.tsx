'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useTranslations } from 'next-intl';
import { Command } from 'lucide-react';
import { useThemeStore } from '@/lib/stores/theme-store';
import { LocaleGreeting } from '@/lib/i18n-provider';
import { subscribeTaskUpdates } from '@/lib/realtime';

interface DashboardShellProps {
  user: {
    name?: string | null;
    email?: string | null;
    role?: string | null;
  };
}

const kpis = [
  { label: 'Velocity', value: '112%', trend: '+6.4%' },
  { label: 'Tasks', value: '342', trend: '+12' },
  { label: 'Incidents', value: '3', trend: '-2' }
];

const columns = [
  { title: 'Alpha Orbit', status: 'In Progress', owner: 'Nia Chen' },
  { title: 'Lunar Relay', status: 'Planning', owner: 'Imran Saeed' },
  { title: 'Europa Ops', status: 'Blocked', owner: 'Maya Ortiz' }
];

export function DashboardShell({ user }: DashboardShellProps) {
  const t = useTranslations('dashboard');
  const { direction, toggle } = useThemeStore();
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    document.body.dir = direction;
  }, [direction]);

  useEffect(() => {
    return subscribeTaskUpdates((payload) => {
      setToast(`Live update: ${JSON.stringify(payload)}`);
      setTimeout(() => setToast(null), 4000);
    });
  }, []);

  return (
    <div className="flex min-h-screen flex-col gap-6 p-6 lg:p-10">
      <header className="glass-card glass-border sticky top-4 z-20 flex items-center justify-between p-4 backdrop-saturate-150">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-slate-300">{t('title')}</p>
          <h1 className="text-2xl font-semibold text-white">
            <LocaleGreeting />
          </h1>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={toggle}
            className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs uppercase tracking-wide text-slate-200 transition hover:bg-white/20"
          >
            {t('rtl')}
          </button>
          <button className="flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-200 shadow-lg shadow-sky-500/20">
            <Command className="h-4 w-4" />⌘K
          </button>
        </div>
      </header>
      <main className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {toast && (
          <motion.div
            className="glass-card glass-border fixed bottom-6 right-6 z-30 max-w-sm px-6 py-4 text-sm text-white"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
          >
            {toast}
          </motion.div>
        )}
        <motion.section
          className="glass-card glass-border col-span-2 space-y-6 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ type: 'spring', stiffness: 120, damping: 18 }}
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm text-slate-300">{user.email}</p>
              <p className="text-lg font-semibold text-white">Role: {user.role ?? 'operator'}</p>
            </div>
            <div className="flex gap-2">
              <input
                placeholder={t('search')}
                className="w-52 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-slate-100 placeholder:text-slate-400"
              />
              <button className="rounded-full border border-white/10 bg-gradient-to-r from-sky-500/30 to-purple-500/30 px-4 py-2 text-sm text-white transition hover:from-sky-500/40 hover:to-purple-500/40">
                {t('filters')}
              </button>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-3">
            {kpis.map((kpi) => (
              <div key={kpi.label} className="glass-card glass-border p-4">
                <p className="text-xs uppercase text-slate-300">{kpi.label}</p>
                <p className="mt-3 text-3xl font-semibold text-white">{kpi.value}</p>
                <p className="text-sm text-emerald-300">{kpi.trend}</p>
              </div>
            ))}
          </div>
          <div className="glass-card glass-border p-4">
            <h2 className="text-lg font-semibold text-white">Mission Projects</h2>
            <div className="mt-4 space-y-3">
              {columns.map((col) => (
                <div
                  key={col.title}
                  className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/5 px-4 py-3 text-sm text-slate-200"
                >
                  <div>
                    <p className="font-medium text-white">{col.title}</p>
                    <p className="text-xs text-slate-300">Owned by {col.owner}</p>
                  </div>
                  <span className="rounded-full bg-emerald-400/20 px-3 py-1 text-xs text-emerald-200">
                    {col.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.section>
        <motion.aside
          className="glass-card glass-border flex flex-col gap-6 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, type: 'spring', stiffness: 120, damping: 18 }}
        >
          <section>
            <h2 className="text-lg font-semibold text-white">Activity</h2>
            <div className="mt-4 space-y-4">
              {['Deploy succeeded', 'Task escalated', 'New document signed'].map((item) => (
                <div key={item} className="rounded-2xl border border-white/5 bg-white/5 p-4 text-sm text-slate-200">
                  {item}
                </div>
              ))}
            </div>
          </section>
          <section>
            <h2 className="text-lg font-semibold text-white">Files</h2>
            <div className="mt-4 space-y-3">
              {['mission-brief.pdf', 'retro-notes.md', 'apollo-sequence.mp4'].map((item) => (
                <div key={item} className="flex items-center justify-between rounded-xl border border-white/5 bg-white/10 px-3 py-2 text-sm text-slate-200">
                  <span>{item}</span>
                  <span className="text-xs text-slate-400">2.4MB</span>
                </div>
              ))}
            </div>
          </section>
        </motion.aside>
      </main>
    </div>
  );
}
