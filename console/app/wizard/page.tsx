import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import WizardClient from './WizardClient';
import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export default async function WizardPage() {
  const setupComplete = await isSetupComplete();
  const session = await getServerSession(authOptions);

  if (setupComplete) {
    if (session) {
      redirect('/console');
    }
    redirect('/login');
  }

  return <WizardClient />;
}
