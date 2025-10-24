'use client';

import { useEffect, useState } from 'react';
import enMessages from '../messages/en.json';
import faMessages from '../messages/fa.json';
import { usePathname, useSearchParams } from 'next/navigation';

const locales = ['en', 'fa'] as const;
type Locale = (typeof locales)[number];

export function useLocaleMessages(pathname?: string) {
  const searchParams = useSearchParams();
  const [locale, setLocale] = useState<Locale>('en');
  const [messages, setMessages] = useState(enMessages);
  const currentPath = pathname ?? usePathname();

  useEffect(() => {
    const urlLocale = (searchParams?.get('locale') as Locale | null) ?? undefined;
    const storageLocale = (typeof window !== 'undefined' ? localStorage.getItem('aionos-locale') : null) as Locale | null;
    const resolvedLocale: Locale = urlLocale && locales.includes(urlLocale) ? urlLocale : storageLocale && locales.includes(storageLocale) ? storageLocale : 'en';
    setLocale(resolvedLocale);
    setMessages(resolvedLocale === 'fa' ? faMessages : enMessages);
  }, [searchParams, currentPath]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('aionos-locale', locale);
    }
  }, [locale]);

  return { locale, messages };
}
