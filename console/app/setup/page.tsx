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

export default function SetupPage() {
  const [selected, setSelected] = useState<ProfileId>('user');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch('/api/setup/profile', { cache: 'no-store' });
        if (!res.ok) return;
        const data = await res.json();
        if (mounted && data?.profile) {
          setSelected(data.profile as ProfileId);
        }
        if (mounted && data?.setupDone) {
          window.location.href = '/';
        }
      } catch (err) {
        console.error('Failed to load profile', err);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const submit = async () => {
    setSaving(true);
    setError('');
    try {
      const res = await fetch('/api/setup/profile', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ profile: selected, setupDone: true }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || 'Failed to save profile');
      }
      window.location.href = '/';
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-lg">Loading profile...</div>;
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
        {error && <p className="text-red-400 text-sm">{error}</p>}
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
