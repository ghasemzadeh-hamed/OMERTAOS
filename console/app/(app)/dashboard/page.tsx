'use client';

import { KPIChip } from '../../../components/KPIChip';
import { GlassCard } from '../../../components/GlassCard';
import { TaskBoard } from '../../../components/TaskBoard';
import { useQuery } from '@tanstack/react-query';
import { listTasks } from '../../../lib/api';
import { useTranslations } from 'next-intl';
import { useStream } from '../../../hooks/useStream';
import { Task } from '../../../types';

export default function DashboardPage() {
  const t = useTranslations('dashboard');
  const { data: tasks = [] } = useQuery({ queryKey: ['tasks'], queryFn: listTasks, staleTime: 5_000 });
  const { data: liveUpdate } = useStream<Task>(`${process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080'}/v1/stream/latest`);

  const mergedTasks = liveUpdate
    ? [liveUpdate, ...tasks.filter((task) => task.taskId !== liveUpdate.taskId)]
    : tasks;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-semibold text-white">{t('welcome')}</h1>
      <div className="grid gap-4 md:grid-cols-4">
        <KPIChip label={t('active_tasks')} value={String(mergedTasks.length)} trend={3.4} />
        <KPIChip label={t('latency')} value="512 ms" trend={-4.2} />
        <KPIChip label={t('budget')} value="$0.08" trend={1.2} />
        <KPIChip label={t('success')} value="99.1%" trend={0.6} />
      </div>
      <GlassCard title="Live tasks" description="Drag across columns as statuses evolve">
        <TaskBoard tasks={mergedTasks} />
      </GlassCard>
    </div>
  );
}
