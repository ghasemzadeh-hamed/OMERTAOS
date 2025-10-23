'use client';

import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { ActivityFeed } from '../../../components/ui/activity-feed';
import { GlassCard } from '../../../components/ui/glass-card';
import { TaskBoard } from '../../../components/ui/task-board';
import { useLocale } from '../../../lib/use-locale';

const fetcher = async () => {
  const response = await fetch('/api/health');
  return response.json();
};

export default function DashboardPage() {
  const { t } = useLocale();
  const { data } = useQuery({ queryKey: ['health'], queryFn: fetcher });
  const router = useRouter();

  useEffect(() => {
    if (!data) return;
  }, [data, router]);

  return (
    <div className="min-h-screen space-y-6 px-8 py-10">
      <motion.header
        className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
      >
        <div>
          <h1 className="text-3xl font-bold">{t('dashboard.title')}</h1>
          <p className="text-slate-300">{t('dashboard.subtitle')}</p>
        </div>
        <div className="flex gap-4">
          <GlassCard title={t('dashboard.tasks')} value="42" trend="+8%" />
          <GlassCard title={t('dashboard.agents')} value="7" trend="+2%" />
        </div>
      </motion.header>
      <section className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TaskBoard />
        </div>
        <ActivityFeed />
      </section>
    </div>
  );
}
