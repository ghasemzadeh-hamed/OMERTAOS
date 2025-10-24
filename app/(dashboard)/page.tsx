import { Suspense } from 'react';
import { DashboardShell } from '@/components/dashboard-shell';
import { getServerAuthSession } from '@/server/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await getServerAuthSession();

  if (!session) {
    redirect('/sign-in');
  }

  return (
    <Suspense fallback={<div className="p-10 text-lg">Loading dashboard…</div>}>
      <DashboardShell user={session.user} />
    </Suspense>
  );
}
