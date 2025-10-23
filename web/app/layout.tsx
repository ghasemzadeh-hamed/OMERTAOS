import './globals.css';
import { Metadata } from 'next';
import { Providers } from '../components/providers';

export const metadata: Metadata = {
  title: 'AION-OS Console',
  description: 'Manage AI agents and tasks across the AION platform.'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
