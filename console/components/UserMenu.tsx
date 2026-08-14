'use client';

import { signOut } from 'next-auth/react';

export default function UserMenu({ email, role }: { email?: string | null; role?: string | null }) {
  return (
    <div className="flex items-center gap-3 text-sm">
      <div className="opacity-80">
        {email ?? 'Unknown'}{' '}
        <span className="opacity-60">({role ?? 'USER'})</span>
      </div>
      <button
        type="button"
        onClick={() => signOut({ callbackUrl: '/login' })}
        className="px-3 py-1.5 rounded-lg border border-white/20 hover:bg-white/10"
      >
        Sign out
      </button>
    </div>
  );
}
