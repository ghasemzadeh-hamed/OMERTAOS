import { ReactNode } from 'react';
import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import NavTabs from '@/components/NavTabs';
import UserMenu from '@/components/UserMenu';

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect('/login');
  }

  const role = (session.user as any)?.role ?? 'USER';

  return (
    <section className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">AION-OS Console</h1>
            <p className="text-sm opacity-70">Operational oversight for agents, tasks, and policies</p>
          </div>
          <UserMenu email={session.user?.email} role={role} />
        </header>
        <NavTabs role={role} />
        <main>{children}</main>
      </div>
    </section>
  );
}
