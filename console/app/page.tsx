import { isRedirectError } from 'next/dist/client/components/redirect';
import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function IndexPage() {
  try {
    let setupComplete = false;
    try {
      setupComplete = await isSetupComplete();
    } catch (error) {
      console.warn('[console] setup detection failed, assuming incomplete', error);
      setupComplete = false;
    }

    if (!setupComplete) {
      redirect('/wizard');
    }

    let session = null;
    try {
      session = await getServerSession(authOptions);
    } catch (error) {
      console.warn('[console] session lookup failed, redirecting to login', error);
      session = null;
    }

    if (!session) {
      redirect('/login');
    }

    redirect('/console');
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
