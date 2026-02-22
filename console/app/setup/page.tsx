'use client';

import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';

const profiles = [
  { id: 'user', label: 'User', description: 'Personal or single operator setup.' },
  { id: 'professional', label: 'Professional', description: 'Team workflows and shared tools.' },
  { id: 'enterprise-vip', label: 'Enterprise-VIP', description: 'Advanced governance and multi-tenant mode.' },
] as const;

type ProfileId = (typeof profiles)[number]['id'];

export default function SetupPage() {
  const router = useRouter();
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('');
  const [totpIssuer, setTotpIssuer] = useState('OMERTAOS');
  const [webauthnRpId, setWebauthnRpId] = useState('localhost');
  const [recoveryEmail, setRecoveryEmail] = useState('admin@local');
  const [profile, setProfile] = useState<ProfileId>('user');
  const [encryptData, setEncryptData] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const submit = useCallback(async () => {
    setError('');
    if (!username.trim() || !password.trim()) {
      setError('Username and password are required.');
      return;
    }

    setSubmitting(true);
    try {
      const res = await fetch('/api/system/setup/bootstrap', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          username: username.trim(),
          password,
          profile,
          encryptData,
          totpIssuer: totpIssuer.trim() || 'OMERTAOS',
          webauthnRpId: webauthnRpId.trim() || 'localhost',
          recoveryEmail: recoveryEmail.trim() || `${username.trim()}@local`,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError((data as any)?.error || 'Unable to save setup.');
        return;
      }
      router.replace('/login');
    } catch {
      setError('Setup service unavailable. Ensure gateway and control are running.');
    } finally {
      setSubmitting(false);
    }
  }, [username, password, profile, encryptData, totpIssuer, webauthnRpId, recoveryEmail, router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 text-white">
      <div className="w-full max-w-4xl space-y-6 rounded-2xl border border-white/10 bg-slate-900/80 p-8 shadow-2xl backdrop-blur-xl">
        <header>
          <h1 className="text-2xl font-semibold">OMERTAOS Initial Setup</h1>
          <p className="text-sm text-white/70">Step 1: security keys, profile, and encryption policy.</p>
        </header>

        <section className="grid gap-4 md:grid-cols-2">
          <label className="space-y-2 text-sm">
            <span>Admin username *</span>
            <input className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2" value={username} onChange={(e) => setUsername(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm">
            <span>Admin password *</span>
            <input type="password" className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2" value={password} onChange={(e) => setPassword(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm">
            <span>TOTP issuer (default)</span>
            <input className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2" value={totpIssuer} onChange={(e) => setTotpIssuer(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm">
            <span>WebAuthn RP ID (default)</span>
            <input className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2" value={webauthnRpId} onChange={(e) => setWebauthnRpId(e.target.value)} />
          </label>
          <label className="space-y-2 text-sm md:col-span-2">
            <span>Recovery email (default)</span>
            <input className="w-full rounded-lg border border-white/10 bg-black/30 px-3 py-2" value={recoveryEmail} onChange={(e) => setRecoveryEmail(e.target.value)} />
          </label>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Choose profile</h2>
          <div className="grid gap-3 md:grid-cols-3">
            {profiles.map((p) => (
              <button key={p.id} onClick={() => setProfile(p.id)} className={`rounded-xl border p-3 text-left ${profile === p.id ? 'border-cyan-400 bg-cyan-500/10' : 'border-white/10 bg-black/20'}`}>
                <div className="font-semibold">{p.label}</div>
                <div className="text-xs text-white/70">{p.description}</div>
              </button>
            ))}
          </div>
          <label className="flex items-center gap-2 text-sm text-white/80">
            <input type="checkbox" checked={encryptData} onChange={(e) => setEncryptData(e.target.checked)} />
            Encrypt stored data
          </label>
        </section>

        <div className="flex items-center justify-between">
          {error ? <p className="text-sm text-rose-300">{error}</p> : <span className="text-xs text-white/60">After confirmation, you will be redirected to login.</span>}
          <button onClick={submit} disabled={submitting} className="rounded-lg bg-cyan-400 px-4 py-2 font-semibold text-slate-950 disabled:opacity-60">
            {submitting ? 'Saving...' : 'Confirm & go to login'}
          </button>
        </div>
      </div>
    </main>
  );
}
