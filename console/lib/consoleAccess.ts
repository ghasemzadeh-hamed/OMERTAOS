import { redirect } from 'next/navigation';

import { fetchProfileState } from '@/lib/profile';
import { safeGetServerSession } from '@/lib/session';

export async function ensureConsoleAccess() {
  const session = await safeGetServerSession();
  if (!session) {
    redirect('/login');
  }

  const role = ((session.user as any)?.role ?? '').toString().toUpperCase();
  if (role !== 'ADMIN') {
    redirect('/login');
  }

  try {
    const profile = await fetchProfileState();
    if (!profile.setupDone) {
      redirect('/setup');
    }
  } catch (error) {
    console.error('[console] Unable to confirm setup state', error);
    redirect('/setup');
  }

  return session;
}
