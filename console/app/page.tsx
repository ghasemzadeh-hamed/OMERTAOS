import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function IndexPage() {
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
}
