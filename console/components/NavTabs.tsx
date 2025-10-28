'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const rolePriority = {
  USER: 0,
  MANAGER: 1,
  ADMIN: 2,
} as const;

type Role = keyof typeof rolePriority;

type Tab = {
  href: string;
  label: string;
  minRole: Role;
};

const tabs: Tab[] = [
  { href: '/dashboard', label: 'Overview', minRole: 'USER' },
  { href: '/dashboard/agents', label: 'Agents', minRole: 'MANAGER' },
  { href: '/dashboard/tasks', label: 'Tasks', minRole: 'USER' },
  { href: '/dashboard/logs', label: 'Logs', minRole: 'MANAGER' },
  { href: '/dashboard/health', label: 'Health', minRole: 'ADMIN' },
];

function hasAccess(role: Role, tab: Tab) {
  return rolePriority[role] >= rolePriority[tab.minRole];
}

function normalizeRole(role?: string | null): Role {
  if (!role) {
    return 'USER';
  }
  const upper = role.toUpperCase() as Role;
  return upper in rolePriority ? upper : 'USER';
}

export default function NavTabs({ role }: { role?: string | null }) {
  const pathname = usePathname();
  const normalizedRole = normalizeRole(role);
  const availableTabs = tabs.filter((tab) => hasAccess(normalizedRole, tab));

  return (
    <div className="flex gap-2 overflow-x-auto">
      {availableTabs.map((tab) => {
        const active = pathname === tab.href || pathname?.startsWith(`${tab.href}/`);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`px-4 py-2 rounded-xl transition border ${
              active ? 'bg-white/15 border-white/20' : 'border-transparent hover:bg-white/10'
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}
