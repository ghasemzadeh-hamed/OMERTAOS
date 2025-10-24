'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';

const navItems = [
  { href: '/dashboard', key: 'dashboard' },
  { href: '/projects', key: 'projects' },
  { href: '/tasks', key: 'tasks' },
  { href: '/agents', key: 'agents', permission: 'canManageAgents' },
  { href: '/policies', key: 'policies', permission: 'canManagePolicies' },
  { href: '/telemetry', key: 'telemetry', permission: 'canViewTelemetry' },
  { href: '/terminal', key: 'terminal', permission: 'canManageAgents' },
  { href: '/settings', key: 'settings' },
];

export function Sidebar() {
  const pathname = usePathname();
  const t = useTranslations('nav');
  const { permissions } = useAuth();

  return (
    <motion.aside
      className="hidden w-64 flex-col gap-2 border-r border-white/10 bg-slate-950/60 p-6 shadow-inner backdrop-blur-3xl md:flex"
      initial={{ opacity: 0, x: -24 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ type: 'spring', stiffness: 120, damping: 18 }}
    >
      <h2 className="text-xl font-semibold">aionOS</h2>
      <nav className="mt-8 flex flex-col gap-2">
        {navItems
          .filter((item) => {
            if (!item.permission) {
              return true;
            }
            return (permissions as any)[item.permission];
          })
          .map((item) => {
            const active = pathname?.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`glass-button flex justify-between ${active ? 'border-white/40 bg-white/20' : ''}`}
              >
                {t(item.key as any)}
              </Link>
            );
          })}
      </nav>
    </motion.aside>
  );
}
