'use client';

import { useEffect } from 'react';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const t = useTranslations('auth');

  useEffect(() => {
    if (status === 'loading') {
      return;
    }
    if (!session) {
      router.replace('/sign-in');
    }
  }, [session, status, router]);

  if (status === 'loading') {
    return (
      <div className="flex h-screen items-center justify-center text-slate-300">
        {t('loading')}
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return <>{children}</>;
}
