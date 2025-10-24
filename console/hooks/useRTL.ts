'use client';

import { useEffect, useState } from 'react';

export function useRTL() {
  const [rtl, setRTL] = useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }
    return localStorage.getItem('aionos-rtl') === 'true';
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      document.body.dir = rtl ? 'rtl' : 'ltr';
      localStorage.setItem('aionos-rtl', rtl ? 'true' : 'false');
    }
  }, [rtl]);

  return { rtl, setRTL };
}
