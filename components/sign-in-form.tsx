'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, LogIn } from 'lucide-react';

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(6)
});

type FormValues = z.infer<typeof schema>;

export function SignInForm() {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (values: FormValues) => {
    setLoading(true);
    setError(null);
    const res = await signIn('credentials', {
      redirect: false,
      email: values.email,
      password: values.password
    });

    if (res?.error) {
      setError(res.error);
    }

    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="text-sm font-medium text-slate-200">Email</label>
        <input
          type="email"
          className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-slate-200 placeholder:text-slate-400 focus:border-glass-accent focus:outline-none"
          placeholder="you@aion.space"
          {...register('email')}
        />
        {errors.email && <p className="mt-1 text-sm text-rose-300">{errors.email.message}</p>}
      </div>
      <div>
        <label className="text-sm font-medium text-slate-200">Password</label>
        <input
          type="password"
          className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 p-3 text-slate-200 placeholder:text-slate-400 focus:border-glass-accent focus:outline-none"
          placeholder="••••••••"
          {...register('password')}
        />
        {errors.password && <p className="mt-1 text-sm text-rose-300">{errors.password.message}</p>}
      </div>
      {error && <div className="rounded-lg bg-rose-500/10 p-3 text-sm text-rose-200">{error}</div>}
      <button
        type="submit"
        disabled={loading}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/10 py-3 text-slate-50 transition hover:bg-white/20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-glass-accent disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />} Sign in
      </button>
      <button
        type="button"
        onClick={() => signIn('google')}
        className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/10 bg-gradient-to-r from-sky-500/30 to-purple-500/30 py-3 text-slate-50 transition hover:from-sky-500/40 hover:to-purple-500/40"
      >
        Continue with Google
      </button>
    </form>
  );
}
