'use client';

import { useMemo } from 'react';

type Mode = 'web' | 'desktop' | 'kiosk';

type Detector = () => Mode;

const defaultDetector: Detector = () => {
  if (typeof navigator !== 'undefined' && navigator.userAgent.includes('Electron')) {
    return 'desktop';
  }
  if (typeof window !== 'undefined' && (window as any).AIONOS_KIOSK === true) {
    return 'kiosk';
  }
  return 'web';
};

export function useEnvMode(detector: Detector = defaultDetector) {
  return useMemo(() => detector(), [detector]);
}
