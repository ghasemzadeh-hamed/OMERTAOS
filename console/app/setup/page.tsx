'use client';

import { useCallback, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { z } from 'zod';

const profileSchema = z.enum(['user', 'professional', 'enterprise-vip']);

const profiles: { id: z.infer<typeof profileSchema>; label: string; description: string }[] = [
  { id: 'user', label: 'Individual', description: 'Personal or small hobby use.' },
  { id: 'professional', label: 'Professional', description: 'Team or business workflows.' },
  { id: 'enterprise-vip', label: 'Enterprise/VIP', description: 'Multi-tenant or advanced control plane.' },
];

export default function SetupPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<z.infer<typeof profileSchema> | ''>('');
  const [error, setError] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);

  const submit = useCallback(async () => {
    setSubmitting(true);
    setError('');
    const parsed = profileSchema.safeParse(profile);
    if (!parsed.success) {
      setError('Please choose a profile to continue.');
      setSubmitting(false);
      return;
    }

    try {
      const res = await fetch('/api/system/setup/profile', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ profile: parsed.data, setupDone: true }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const message =
          typeof (data as any)?.error === 'string'
            ? (data as any).error
            : 'Unable to save your selection. Please try again.';
        const hint = (data as any)?.hint;
        setError(`${message}${hint && process.env.NODE_ENV !== 'production' ? ` (${hint})` : ''}`);
        return;
      }
      router.replace('/login');
    } catch (err) {
      setError('Gateway or console API unavailable. Ensure the gateway is running.');
    } finally {
      setSubmitting(false);
    }
  }, [profile, router]);

  const buttons = useMemo(
    () =>
      profiles.map((p) => (
        <button
          key={p.id}
          onClick={() => setProfile(p.id)}
          className={`w-full rounded-lg border border-white/10 p-4 text-left transition hover:border-emerald-400/70 hover:text-emerald-200 ${
            profile === p.id ? 'bg-emerald-500/10 border-emerald-400 text-emerald-100' : 'bg-slate-900'
          }`}
        >
          <div className="text-lg font-semibold">{p.label}</div>
          <div className="text-sm text-white/70">{p.description}</div>
        </button>
      )),
    [profile],
  );

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
      <div className="w-full max-w-3xl space-y-6 rounded-2xl border border-white/10 bg-slate-900/80 p-8 shadow-2xl">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">Welcome to aionOS Console</h1>
          <p className="text-sm text-white/70">Choose how you plan to use the console to finish setup.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">{buttons}</div>
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm text-white/60">You can change this later in Admin Config.</p>
          <button
            onClick={submit}
            disabled={submitting}
            className="rounded-md bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow hover:bg-emerald-400 disabled:opacity-60"
          >
            {submitting ? 'Saving…' : 'Continue'}
          </button>
        </div>
        {error ? <p className="text-sm text-rose-300">{error}</p> : null}
      </div>
    </main>
  );
}
