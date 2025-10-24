'use client';

import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { fetchPolicy, reloadRouterPolicy, updatePolicy } from '../lib/api';
import { useTranslations } from 'next-intl';
import { toast } from 'sonner';

const schema = z.object({
  budget: z.object({
    default_usd: z.number().min(0),
    hard_cap_usd: z.number().min(0),
  }),
  latency: z.object({
    local: z.number().min(0),
    api: z.number().min(0),
    hybrid: z.number().min(0),
  }),
});

type PolicyForm = z.infer<typeof schema>;

export function PolicyEditor() {
  const t = useTranslations('policies');
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ['policy'], queryFn: fetchPolicy });

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PolicyForm>({ resolver: zodResolver(schema), values: data as PolicyForm | undefined });

  const mutation = useMutation({
    mutationFn: updatePolicy,
    onSuccess: async () => {
      toast.success(t('success'));
      await queryClient.invalidateQueries({ queryKey: ['policy'] });
      await reloadRouterPolicy();
    },
    onError: () => toast.error(t('error')),
  });

  const onSubmit = (values: PolicyForm) => {
    mutation.mutate(values);
  };

  return (
    <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label className="block text-sm text-slate-200">Budget default (USD)</label>
        <input type="number" step="0.01" className="glass-input" {...register('budget.default_usd', { valueAsNumber: true })} />
        {errors.budget?.default_usd ? <p className="text-xs text-rose-300">{errors.budget.default_usd.message}</p> : null}
      </div>
      <div>
        <label className="block text-sm text-slate-200">Budget hard cap (USD)</label>
        <input type="number" step="0.01" className="glass-input" {...register('budget.hard_cap_usd', { valueAsNumber: true })} />
        {errors.budget?.hard_cap_usd ? <p className="text-xs text-rose-300">{errors.budget.hard_cap_usd.message}</p> : null}
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <label className="block text-sm text-slate-200">
          Local P95 (ms)
          <input type="number" className="glass-input" {...register('latency.local', { valueAsNumber: true })} />
          {errors.latency?.local ? <p className="text-xs text-rose-300">{errors.latency.local.message}</p> : null}
        </label>
        <label className="block text-sm text-slate-200">
          API P95 (ms)
          <input type="number" className="glass-input" {...register('latency.api', { valueAsNumber: true })} />
          {errors.latency?.api ? <p className="text-xs text-rose-300">{errors.latency.api.message}</p> : null}
        </label>
        <label className="block text-sm text-slate-200">
          Hybrid P95 (ms)
          <input type="number" className="glass-input" {...register('latency.hybrid', { valueAsNumber: true })} />
          {errors.latency?.hybrid ? <p className="text-xs text-rose-300">{errors.latency.hybrid.message}</p> : null}
        </label>
      </div>
      <div className="flex items-center gap-3">
        <button type="submit" className="glass-button">
          {t('save')}
        </button>
        <button type="button" className="glass-button" onClick={() => reset()}>
          {t('reset')}
        </button>
      </div>
    </form>
  );
}
