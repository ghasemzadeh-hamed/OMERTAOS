'use client';

import { useRouter, useSearchParams } from 'next/navigation';

export function useLocaleToggle() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const locale = searchParams?.get('locale') ?? 'en';

  const toggle = () => {
    const nextLocale = locale === 'fa' ? 'en' : 'fa';
    const params = new URLSearchParams(searchParams?.toString());
    params.set('locale', nextLocale);
    router.replace(`?${params.toString()}`);
  };

  return { locale, toggle };
}
