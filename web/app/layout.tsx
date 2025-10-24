import type { Metadata } from 'next'
import './globals.css'
import { Providers } from '../components/providers'
import { CommandPalette } from '../components/command-palette'

export const metadata: Metadata = {
  title: 'AION-OS Console',
  description: 'Glassmorphism control surface for AI agents'
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-theme="dark">
      <body className="min-h-screen">
        <Providers>
          {children}
          <CommandPalette />
        </Providers>
      </body>
    </html>
  )
}
