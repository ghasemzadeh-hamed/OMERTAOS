import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export default function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center">
      <section className="glass-panel p-12 w-full max-w-2xl text-center space-y-6">
        <h1 className="text-4xl font-bold tracking-tight">Welcome to AION-OS</h1>
        <p className="text-lg text-slate-300">
          Deploy, orchestrate, and monitor modular AI agents with a real-time glassmorphism control center.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 rounded-full border border-accent/70 bg-white/10 px-5 py-3 text-lg font-semibold text-white shadow-lg transition hover:scale-105 hover:bg-accent/20"
          >
            Sign in
            <ArrowRight className="h-5 w-5" />
          </Link>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-full border border-white/20 px-5 py-3 text-lg font-semibold text-slate-200 transition hover:scale-105 hover:bg-white/10"
          >
            Explore dashboard
          </Link>
        </div>
      </section>
    </main>
  );
}
