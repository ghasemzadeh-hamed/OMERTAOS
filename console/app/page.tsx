import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export default async function IndexPage() {
  const setupComplete = await isSetupComplete();
  const session = await getServerSession(authOptions);

  if (!setupComplete) {
    redirect('/wizard');
  }

  if (!session) {
    redirect('/login');
  }

  redirect('/console');
}
