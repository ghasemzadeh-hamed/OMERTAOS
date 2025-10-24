'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createTask, listTasks } from '../../../lib/api';
import { GlassCard } from '../../../components/GlassCard';
import { TaskBoard } from '../../../components/TaskBoard';
import { useTranslations } from 'next-intl';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { useState } from 'react';

interface TaskForm {
  intent: string;
  params: string;
  preferred_engine?: string;
  privacy?: string;
}

export default function TasksPage() {
  const { data: tasks = [] } = useQuery({ queryKey: ['tasks'], queryFn: listTasks });
  const queryClient = useQueryClient();
  const t = useTranslations('tasks');
  const [rateLimited, setRateLimited] = useState(false);

  const { register, handleSubmit, reset } = useForm<TaskForm>({
    defaultValues: {
      intent: 'summarize',
      params: JSON.stringify({ text: 'Explain the router decision policy.' }, null, 2),
      preferred_engine: 'auto',
      privacy: 'allow-api',
    },
  });

  const mutation = useMutation({
    mutationFn: createTask,
    onError: (error: Error) => {
      if (/429/.test(error.message)) {
        setRateLimited(true);
      }
      toast.error(error.message);
    },
    onSuccess: async () => {
      setRateLimited(false);
      toast.success('Task submitted');
      await queryClient.invalidateQueries({ queryKey: ['tasks'] });
      reset();
    },
  });

  const onSubmit = handleSubmit((values) => {
    try {
      const params = JSON.parse(values.params);
      mutation.mutate({
        intent: values.intent,
        params,
        preferredEngine: values.preferred_engine,
        sla: { privacy: values.privacy },
      } as any);
    } catch (error) {
      toast.error('Parameters must be valid JSON');
    }
  });

  return (
    <div className="space-y-6">
      <GlassCard
        title={t('create')}
        description="Submit a new orchestration task"
        action={<button className="glass-button" onClick={onSubmit}>{t('submit')}</button>}
      >
        <form className="grid gap-4 md:grid-cols-2" onSubmit={onSubmit}>
          <label className="block text-sm text-slate-200">
            {t('intent')}
            <input className="glass-input" {...register('intent')} />
          </label>
          <label className="block text-sm text-slate-200">
            {t('preferred_engine')}
            <select className="glass-input" {...register('preferred_engine')}>
              <option value="auto">Auto</option>
              <option value="local">Local</option>
              <option value="api">API</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </label>
          <label className="block text-sm text-slate-200">
            {t('privacy')}
            <select className="glass-input" {...register('privacy')}>
              <option value="allow-api">Allow API</option>
              <option value="local-only">Local only</option>
              <option value="hybrid">Hybrid</option>
            </select>
          </label>
          <label className="md:col-span-2 text-sm text-slate-200">
            {t('params')}
            <textarea rows={6} className="glass-input" {...register('params')} />
          </label>
        </form>
        {rateLimited ? <p className="text-xs text-amber-300">{t('rate_limited')}</p> : null}
      </GlassCard>
      <TaskBoard tasks={tasks} />
    </div>
  );
}
