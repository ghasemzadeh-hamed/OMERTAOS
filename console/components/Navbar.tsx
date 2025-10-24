'use client';

import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { useTranslations } from 'next-intl';
import { ThemeToggle } from './ThemeToggle';
import { useLocaleToggle } from '../lib/i18n';
import { useUIStore } from '../state/ui.store';
import { Command } from 'lucide-react';

export function Navbar() {
  const { session, signOut } = useAuth();
  const t = useTranslations('nav');
  const { toggle, locale } = useLocaleToggle();
  const togglePalette = useUIStore((state) => state.toggleCommandPalette);

  return (
    <motion.nav
      className="sticky top-0 z-20 flex items-center justify-between rounded-3xl border border-white/10 bg-slate-900/50 px-6 py-3 shadow-glass backdrop-blur-2xl"
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: 'spring', stiffness: 120, damping: 18 }}
    >
      <div className="flex items-center gap-3">
        <button
          className="glass-button flex items-center gap-2"
          onClick={togglePalette}
          aria-label={t('command_palette')}
        >
          <Command className="h-4 w-4" />
          <span className="hidden md:inline">⌘K</span>
        </button>
        <button className="glass-button" onClick={toggle}>
          {locale === 'fa' ? 'FA' : 'EN'}
        </button>
        <ThemeToggle />
      </div>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-slate-200">{session?.user?.email}</span>
        <button className="glass-button" onClick={() => signOut()}>
          {t('sign_out')}
        </button>
      </div>
    </motion.nav>
  );
}
