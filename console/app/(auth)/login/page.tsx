'use client';

import { useState } from 'react';
import { signIn } from 'next-auth/react';
import { useRouter, useSearchParams } from 'next/navigation';
import GlassCard from '@/components/GlassCard';

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);

    const callbackUrl = searchParams.get('callbackUrl') ?? '/dashboard';
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

    alert('Invalid username or password');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white grid place-items-center p-6">
      <GlassCard className="w-full max-w-md">
        <h1 className="text-2xl font-semibold mb-6">Sign in</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Username or Email</label>
            <input
              type="text"
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg p-3 outline-none focus:ring-2 focus:ring-white/30"
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full bg-white/10 border border-white/20 rounded-lg p-3 outline-none focus:ring-2 focus:ring-white/30"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-white/15 hover:bg-white/20 border border-white/30"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </GlassCard>
    </div>
  );
}
