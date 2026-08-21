import { redirect } from 'next/navigation';

import { safeGetServerSession } from '@/lib/session';
import { isSetupComplete } from '@/lib/setup';

export async function ensureConsoleAccess() {
  const session = await safeGetServerSession();
  if (!session) {
    redirect('/login');
  }

  const role = ((session.user as any)?.role ?? '').toString().toUpperCase();
  if (role !== 'ADMIN') {
    redirect('/login');
  }

  if (!(await isSetupComplete())) {
    redirect('/setup');
  }

  return session;
}
