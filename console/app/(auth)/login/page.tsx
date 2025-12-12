import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

import LoginForm from './LoginForm';
import { authOptions } from '@/lib/auth';
import { isSetupComplete } from '@/lib/setup';

export default async function LoginPage() {
  const setupComplete = await isSetupComplete();
  if (!setupComplete) {
    redirect('/setup');
  }

  const session = await getServerSession(authOptions);
  if (session) {
    redirect('/');
  }

  const defaultHint =
    process.env.CONSOLE_ADMIN_EMAIL && process.env.CONSOLE_ADMIN_PASSWORD
      ? `Default admin: ${process.env.CONSOLE_ADMIN_EMAIL} / ${process.env.CONSOLE_ADMIN_PASSWORD}`
      : 'Use the admin credentials you configured earlier.';

  return <LoginForm defaultHint={defaultHint} />;
}
