import type { Metadata } from 'next';
import '../styles/globals.css';
import '../styles/glass.css';
import { ThemeProvider } from '../providers/ThemeProvider';
import { QueryProvider } from '../providers/QueryProvider';
import { I18nProvider } from '../providers/I18nProvider';
import { Toaster } from 'sonner';
import { AuthProvider } from '../providers/AuthProvider';

export const metadata: Metadata = {
  title: 'aionOS Console',
  description: 'Glass UI console for the aionOS platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="bg-slate-950 text-slate-100 antialiased">
        <I18nProvider>
          <ThemeProvider>
            <AuthProvider>
              <QueryProvider>
                {children}
                <Toaster richColors position="bottom-right" closeButton />
              </QueryProvider>
            </AuthProvider>
          </ThemeProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
