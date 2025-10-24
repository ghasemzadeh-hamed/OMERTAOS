import { ReactNode } from 'react';
import { Navbar } from '../../components/Navbar';
import { Sidebar } from '../../components/Sidebar';
import { CommandPalette } from '../../components/CommandPalette';
import { AuthGuard } from '../../components/AuthGuard';
import { ToastViewport } from '../../components/ToastViewport';

export default function AppLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex h-screen bg-slate-950 text-slate-100">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Navbar />
          <main className="flex-1 overflow-y-auto px-6 py-6 backdrop-blur-xl">
            <div className="mx-auto max-w-7xl space-y-6">{children}</div>
          </main>
        </div>
        <CommandPalette />
        <ToastViewport />
      </div>
    </AuthGuard>
  );
}
