import { isRedirectError } from 'next/dist/client/components/redirect';
import { redirect } from 'next/navigation';

import { dashboardPage, findNavById } from '@/lib/ui-registry';
import { resolveBootstrapState } from '../../packages/ui-core/src/bootstrap';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

async function fetchDashboardHealth() {
  const res = await fetch(`${process.env.NEXTAUTH_URL || ''}/api/system/health`, { cache: 'no-store' }).catch(() => null);
  if (!res?.ok) return null;
  return res.json();
}

function readField(input: any, path: string) {
  return path.split('.').reduce((acc, key) => (acc as any)?.[key], input ?? undefined);
}

export default async function IndexPage() {
  try {
    const bootstrap = await resolveBootstrapState(process.env.NEXTAUTH_URL || undefined);
    if (!bootstrap.setupDone) {
      redirect('/setup');
    }
    if (bootstrap.setupDone && !bootstrap.authenticated) {
      redirect('/login');
    }
    if (bootstrap.setupDone && bootstrap.authenticated && !bootstrap.onboardingComplete) {
      redirect('/onboarding');
    }

    const health = await fetchDashboardHealth();
    const page = dashboardPage();

    return (
      <main className="min-h-screen bg-slate-950 text-white">
        <section className="border-b border-white/5 bg-slate-900/60 px-8 py-6">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-sm text-white/70">Welcome back to the OMERTAOS console.</p>
        </section>
        <section className="grid gap-4 px-8 py-6 md:grid-cols-3">
          {page.widgets.map((widget) => {
            const value = readField(health, widget.field);
            return (
              <div key={widget.id} className="rounded-xl border border-white/10 bg-slate-900/70 p-4">
                <h2 className="text-sm font-semibold text-white/80">{widget.title}</h2>
                <p className="mt-2 text-lg font-semibold">{typeof value === 'object' ? value?.status ?? 'unknown' : value ?? 'unknown'}</p>
                <p className="text-sm text-white/60">{widget.description}</p>
              </div>
            );
          })}
        </section>
        <section className="grid gap-4 px-8 pb-10 md:grid-cols-2">
          <div className="rounded-xl border border-white/10 bg-slate-900/70 p-4">
            <h3 className="text-sm font-semibold text-white/80">Quick links</h3>
            <ul className="mt-3 space-y-2 text-sm text-emerald-200">
              {page.quickLinks.map((link) => {
                const nav = findNavById(link.navigationRef);
                if (!nav) return null;
                return (
                  <li key={link.id}>
                    <a className="hover:text-emerald-100" href={nav.path}>
                      {nav.label}
                    </a>
                  </li>
                );
              })}
            </ul>
          </div>
          <div className="rounded-xl border border-white/10 bg-slate-900/70 p-4">
            <h3 className="text-sm font-semibold text-white/80">Session</h3>
            <p className="mt-2 text-sm text-white/70">Gated by shared bootstrap state.</p>
            <a className="mt-3 inline-block text-sm text-emerald-200 hover:text-emerald-100" href="/exit">
              Log out
            </a>
          </div>
        </section>
      </main>
    );
  } catch (error) {
    if (isRedirectError(error)) {
      throw error;
    }
    console.error('[console] root page fallback after error', error);
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <div className="space-y-3 text-center">
          <h1 className="text-xl font-semibold">Console is starting</h1>
          <p className="text-sm text-white/70">
            We could not complete the normal redirect flow. Try visiting the login page directly.
          </p>
          <a className="text-emerald-200 hover:text-emerald-100" href="/login">
            Go to login
          </a>
        </div>
      </main>
    );
  }
}
