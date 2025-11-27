'use client';

import Link from 'next/link';
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, Suspense, useState } from 'react';

import GlassPanel from '@/components/GlassPanel';

export default function LoginForm({ defaultHint }: { defaultHint?: string }) {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    const callbackUrl = searchParams?.get('callbackUrl') ?? '/console';
    const result = await signIn('credentials', {
      identifier,
      password,
      redirect: false,
      callbackUrl,
    });

    setLoading(false);

    if (result?.ok && result.url) {
      router.push(result.url);
      return;
    }

    setError('Invalid email or password.');
  };

  return (
    <Suspense fallback={null}>
      <main className="min-h-dvh grid place-items-center p-6 text-white" dir="ltr">
        <GlassPanel className="w-full max-w-sm space-y-6 p-6">
          <div className="text-center space-y-1">
            <h1 className="text-2xl font-semibold text-white/90">Sign in to AION-OS</h1>
            <p className="text-sm text-white/60">
              Use the admin account created during setup.
              {defaultHint ? ` ${defaultHint}` : ''}
            </p>
          </div>
          <form onSubmit={onSubmit} className="space-y-4" noValidate>
            <div className="space-y-2 text-left">
              <label htmlFor="identifier" className="text-sm text-white/80">
                Email
              </label>
              <input
                id="identifier"
                name="identifier"
                type="text"
                autoComplete="username"
                required
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                className="glass-input placeholder:text-white/40"
              />
            </div>
            <div className="space-y-2 text-left">
              <label htmlFor="password" className="text-sm text-white/80">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="glass-input placeholder:text-white/40"
              />
            </div>
            {error ? <p className="text-sm text-rose-300 text-left">{error}</p> : null}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-white/20 py-2.5 font-medium text-white transition hover:bg-white/30 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
          <div className="text-center text-sm text-white/70">
            <Link href="/wizard" className="font-medium text-white hover:text-white/90">
              Back to setup
            </Link>
          </div>
        </GlassPanel>
      </main>
    </Suspense>
  );
}
