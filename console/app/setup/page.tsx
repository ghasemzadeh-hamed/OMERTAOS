'use client';

import { useEffect, useState } from 'react';

const profiles = [
  {
    id: 'user',
    title: 'User',
    description: 'Quickstart, local LLM, minimal services.',
  },
  {
    id: 'professional',
    title: 'Professional',
    description: 'Explorer, Terminal, IoT bridge, team workflows.',
  },
  {
    id: 'enterprise-vip',
    title: 'Enterprise-VIP',
    description: 'GPU, SEAL self-adaptation, policy controls.',
  },
] as const;

type ProfileId = (typeof profiles)[number]['id'];

type ProfileError = {
  message: string;
  hint?: string;
  status?: number;
};

export default function SetupPage() {
  const [selected, setSelected] = useState<ProfileId>('user');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ProfileError | null>(null);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/setup/profile', { cache: 'no-store' });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const message = typeof data?.error === 'string' ? data.error : 'Unable to load setup state';
        const hint = typeof data?.hint === 'string' ? data.hint : undefined;
        throw { message, hint, status: res.status } as ProfileError;
      }
      if (data?.profile) {
        setSelected(data.profile as ProfileId);
      }
      if (data?.setupDone) {
        window.location.href = '/';
        return;
      }
    } catch (err) {
      console.error('Failed to load profile', err);
      const fallback: ProfileError = {
        message: err && typeof err === 'object' && 'message' in err && typeof (err as any).message === 'string'
          ? (err as any).message
          : 'Failed to load setup state',
        hint: err && typeof err === 'object' && 'hint' in err && typeof (err as any).hint === 'string'
          ? (err as any).hint
          : undefined,
        status:
          err && typeof err === 'object' && 'status' in err && typeof (err as any).status === 'number'
            ? (err as any).status
            : undefined,
      };
      setError(fallback);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const submit = async () => {
    setSaving(true);
    setError(null);
    try {
      const res = await fetch('/api/setup/profile', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ profile: selected, setupDone: true }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        const message = typeof data?.error === 'string' ? data.error : 'Failed to save profile';
        const hint = typeof data?.hint === 'string' ? data.hint : undefined;
        throw { message, hint, status: res.status } as ProfileError;
      }
      window.location.href = '/';
    } catch (err) {
      console.error(err);
      const fallback: ProfileError = {
        message: err && typeof err === 'object' && 'message' in err && typeof (err as any).message === 'string'
          ? (err as any).message
          : 'Failed to save profile',
        hint: err && typeof err === 'object' && 'hint' in err && typeof (err as any).hint === 'string'
          ? (err as any).hint
          : undefined,
        status:
          err && typeof err === 'object' && 'status' in err && typeof (err as any).status === 'number'
            ? (err as any).status
            : undefined,
      };
      setError(fallback);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-lg text-slate-200">
        <div className="flex items-center gap-3">
          <span className="h-5 w-5 animate-spin rounded-full border-2 border-cyan-400 border-t-transparent" />
          <span>Loading setup profile…</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-100 p-6">
      <div className="w-full max-w-4xl space-y-6">
        <header className="space-y-2 text-center">
          <h1 className="text-3xl font-semibold">Select Kernel Profile</h1>
          <p className="text-sm text-slate-300">
            Choose how AION-OS should orchestrate services on this node.
          </p>
        </header>
        <div className="grid gap-4 md:grid-cols-3">
          {profiles.map((profile) => (
            <label
              key={profile.id}
              className={`glass-card cursor-pointer border transition ${
                selected === profile.id ? 'border-cyan-400 shadow-cyan-500/40' : 'border-transparent opacity-80'
              }`}
            >
              <input
                type="radio"
                className="sr-only"
                name="profile"
                value={profile.id}
                checked={selected === profile.id}
                onChange={() => setSelected(profile.id)}
              />
              <div className="space-y-2 p-6">
                <h2 className="text-xl font-medium">{profile.title}</h2>
                <p className="text-sm text-slate-300">{profile.description}</p>
              </div>
            </label>
          ))}
        </div>
        {error && (
          <div className="space-y-2 rounded-md border border-red-500/40 bg-red-950/40 p-3 text-sm text-red-100">
            <p className="font-medium text-red-200">{error.message}</p>
            {error.status ? <p className="text-xs text-red-200/80">Gateway status: {error.status}</p> : null}
            {error.hint ? <p className="text-xs text-red-100/80">{error.hint}</p> : null}
            <button
              className="mt-1 inline-flex items-center gap-2 rounded-md bg-red-500/20 px-3 py-1 text-xs font-semibold text-red-100 hover:bg-red-500/30"
              onClick={loadProfile}
              type="button"
            >
              Retry
            </button>
          </div>
        )}
        <div className="flex justify-end">
          <button
            onClick={submit}
            disabled={saving}
            className="px-6 py-2 rounded-md bg-cyan-500 text-slate-900 font-semibold disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}
