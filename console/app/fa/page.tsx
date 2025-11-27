import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export default async function PersianHomeRedirect() {
  const setupComplete = await isSetupComplete();
  const session = await getServerSession(authOptions);

  if (!setupComplete) {
    redirect('/fa/wizard');
  }

  if (!session) {
    redirect('/fa/login');
  }

  redirect('/fa/console');
}
