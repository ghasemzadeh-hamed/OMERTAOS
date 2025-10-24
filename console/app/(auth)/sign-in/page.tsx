'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import Link from 'next/link';

export default function SignInPage() {
  const t = useTranslations('auth');
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    const result = await signIn('credentials', {
      redirect: false,
      email,
      password,
    });
    setLoading(false);
    if (result?.error) {
      setError(result.error);
      return;
    }
    router.push('/dashboard');
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 via-slate-950 to-black">
      <motion.div
        className="glass-card w-full max-w-md p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ type: 'spring', stiffness: 120, damping: 20 }}
      >
        <h1 className="text-3xl font-semibold mb-6">{t('title')}</h1>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-200">{t('email')}</span>
            <input
              className="glass-input"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
              placeholder="user@example.com"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block text-slate-200">{t('password')}</span>
            <input
              className="glass-input"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <p className="text-sm text-red-400">{error}</p> : null}
          <button type="submit" className="glass-button w-full" disabled={loading}>
            {loading ? t('loading') : t('submit')}
          </button>
        </form>
        <div className="mt-6 space-y-2">
          <button className="glass-button w-full" onClick={() => signIn('google')}>
            {t('signin_google')}
          </button>
          <Link href="/" className="block text-center text-sm text-slate-300 hover:text-white">
            {t('back_home')}
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
