'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode, useMemo } from 'react';
import { ThemeProvider } from 'next-themes';
import { SessionProvider } from 'next-auth/react';
import { I18nProviderClient } from '@/lib/i18n-provider';
import { useThemeStore } from '@/lib/stores/theme-store';

export function Providers({ children }: { children: ReactNode }) {
  const queryClient = useMemo(() => new QueryClient(), []);
  const { direction } = useThemeStore();

  return (
    <SessionProvider>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
          <I18nProviderClient direction={direction}>{children}</I18nProviderClient>
        </ThemeProvider>
      </QueryClientProvider>
    </SessionProvider>
  );
}
