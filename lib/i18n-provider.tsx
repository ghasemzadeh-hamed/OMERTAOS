'use client';

import { NextIntlClientProvider, useTranslations } from 'next-intl';
import { ReactNode, useMemo } from 'react';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import en from '@/messages/en.json';
import fa from '@/messages/fa.json';

interface Props {
  children: ReactNode;
  direction: 'ltr' | 'rtl';
}

export function I18nProviderClient({ children, direction }: Props) {
  const pathname = usePathname();
  const messages = useMemo(() => (direction === 'rtl' ? fa : en), [direction]);
  return (
    <NextIntlClientProvider locale={direction === 'rtl' ? 'fa' : 'en'} messages={messages}>
      <div dir={direction} className="transition-[direction] duration-300">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ type: 'spring', stiffness: 120, damping: 20 }}
          >
            {children}
          </motion.div>
        </AnimatePresence>
      </div>
    </NextIntlClientProvider>
  );
}

export function LocaleGreeting() {
  const t = useTranslations('dashboard');
  return <span>{t('welcome', { name: 'AION Operator' })}</span>;
}
