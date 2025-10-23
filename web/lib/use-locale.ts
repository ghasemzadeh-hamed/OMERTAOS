'use client';

import en from '../locales/en/common.json';
import fa from '../locales/fa/common.json';

type Dictionary = typeof en;

const dictionaries: Record<string, Dictionary> = {
  en,
  fa
};

export function useLocale() {
  const locale = typeof document !== 'undefined' ? document.documentElement.lang || 'en' : 'en';
  const dictionary = dictionaries[locale] ?? en;
  return {
    t: (key: string, values?: Record<string, string | number>) => {
      const value = key.split('.').reduce<any>((acc, part) => (acc ? acc[part] : undefined), dictionary);
      if (typeof value !== 'string') {
        return key;
      }
      return value.replace(/\{(\w+)\}/g, (_, token) => String(values?.[token] ?? ''));
    },
    locale
  };
}
