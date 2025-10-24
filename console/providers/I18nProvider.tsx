'use client';

import { NextIntlClientProvider } from 'next-intl';
import { ReactNode, useEffect } from 'react';
import { useLocaleMessages } from '../hooks/useLocaleMessages';

export function I18nProvider({ children }: { children: ReactNode }) {
  const { locale, messages } = useLocaleMessages();

  useEffect(() => {
    document.documentElement.dir = locale === 'fa' ? 'rtl' : 'ltr';
    document.documentElement.lang = locale;
  }, [locale]);

  return (
    <NextIntlClientProvider locale={locale} messages={messages} timeZone="UTC">
      {children}
    </NextIntlClientProvider>
  );
}
