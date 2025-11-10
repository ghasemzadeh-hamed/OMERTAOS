'use client';

import { NextIntlClientProvider } from 'next-intl';
import { ReactNode, Suspense, useEffect } from 'react';
import { useLocaleMessages } from '../hooks/useLocaleMessages';

function I18nProviderInner({ children }: { children: ReactNode }) {
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

export function I18nProvider({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={null}>
      <I18nProviderInner>{children}</I18nProviderInner>
    </Suspense>
  );
}
