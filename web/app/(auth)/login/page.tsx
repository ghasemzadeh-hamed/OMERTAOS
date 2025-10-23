'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

type FormValues = z.infer<typeof schema>;

export default function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [loading, setLoading] = useState(false);

  const onSubmit = async (values: FormValues) => {
    setLoading(true);
    await signIn('credentials', { ...values, callbackUrl: '/dashboard' });
    setLoading(false);
  };

  return (
    <div className="flex min-h-screen items-center justify-center">
      <motion.form
        onSubmit={handleSubmit(onSubmit)}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25, type: 'spring' }}
        className="glass-panel-dark w-full max-w-md space-y-6 px-10 py-12"
      >
        <header className="space-y-2 text-center">
          <h1 className="text-3xl font-semibold">Sign in</h1>
          <p className="text-slate-300">Access your AI command center.</p>
        </header>
        <div className="space-y-4 text-left">
          <div>
            <label htmlFor="email" className="text-sm uppercase tracking-wide text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="mt-2 w-full rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent"
              {...register('email')}
            />
            {errors.email && <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>}
          </div>
          <div>
            <label htmlFor="password" className="text-sm uppercase tracking-wide text-slate-300">
              Password
            </label>
            <input
              id="password"
              type="password"
              className="mt-2 w-full rounded-xl border border-white/10 bg-white/10 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-accent"
              {...register('password')}
            />
            {errors.password && <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>}
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-full border border-accent/50 bg-accent/30 px-4 py-3 font-semibold text-white shadow-lg transition hover:scale-[1.01] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
          <button
            type="button"
            onClick={() => signIn('google', { callbackUrl: '/dashboard' })}
            className="w-full rounded-full border border-white/20 bg-white/5 px-4 py-3 font-semibold text-white transition hover:bg-white/10"
          >
            Continue with Google
          </button>
        </div>
      </motion.form>
    </div>
  );
}
