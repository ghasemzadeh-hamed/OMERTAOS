import './globals.css';
import type { Metadata } from 'next';
import { Inter, Vazirmatn } from 'next/font/google';
import { ReactNode } from 'react';
import { Providers } from '@/components/providers';

const inter = Inter({ subsets: ['latin'] });
const vazir = Vazirmatn({ subsets: ['arabic'], variable: '--font-vazir' });

export const metadata: Metadata = {
  title: 'AION Dashboard',
  description: 'Glassmorphism operations control center for cross-team productivity.'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={`${inter.className} ${vazir.variable}`} suppressHydrationWarning>
      <body className="min-h-screen bg-slate-950/90 text-slate-100">
        <Providers>
          <div className="relative min-h-screen">
            <div className="pointer-events-none fixed inset-0 -z-10 bg-[radial-gradient(circle_at_20%_20%,rgba(96,165,250,0.25),transparent_55%),radial-gradient(circle_at_80%_0%,rgba(244,114,182,0.2),transparent_50%),linear-gradient(180deg,rgba(15,23,42,0.95),rgba(15,23,42,0.8))]" />
            {children}
          </div>
        </Providers>
      </body>
    </html>
  );
}
