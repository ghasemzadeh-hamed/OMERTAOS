'use client';

import { useEffect, useState } from 'react';

export function useRTL() {
  const [rtl, setRTL] = useState(() => {
    if (typeof window === 'undefined') {
      return false;
    }
    return localStorage.getItem('aion-rtl') === 'true';
  });

  useEffect(() => {
    if (typeof window !== 'undefined') {
      document.body.dir = rtl ? 'rtl' : 'ltr';
      localStorage.setItem('aion-rtl', rtl ? 'true' : 'false');
    }
  }, [rtl]);

  return { rtl, setRTL };
}
