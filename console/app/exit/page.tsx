'use client';

import { useEffect } from 'react';
import { signOut } from 'next-auth/react';

export default function ExitPage() {
  useEffect(() => {
    signOut({ callbackUrl: '/login' }).catch((error) => console.error('[console] sign out failed', error));
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
      <div className="space-y-3 text-center">
        <h1 className="text-xl font-semibold">Signing you out…</h1>
        <p className="text-sm text-white/70">Finishing session cleanup.</p>
      </div>
    </main>
  );
}
