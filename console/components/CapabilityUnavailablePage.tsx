import Link from 'next/link';
import { AlertTriangle } from 'lucide-react';

import { Button } from '@/components/ui/button';

type CapabilityUnavailablePageProps = {
  title: string;
  description: string;
  reason: string;
};

export default function CapabilityUnavailablePage({ title, description, reason }: CapabilityUnavailablePageProps) {
  return (
    <main className="min-h-dvh bg-slate-950 px-4 py-8 text-white">
      <div className="mx-auto max-w-3xl space-y-6">
        <header className="border-b border-white/10 pb-5">
          <h1 className="text-2xl font-semibold">{title}</h1>
          <p className="mt-1 text-sm text-white/60">{description}</p>
        </header>
        <section className="flex items-start gap-3 border border-amber-400/30 bg-amber-400/10 p-4">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
          <div>
            <h2 className="font-medium">Capability unavailable</h2>
            <p className="mt-1 text-sm leading-6 text-white/65">{reason}</p>
          </div>
        </section>
        <div className="flex gap-2">
          <Button asChild><Link href="/console">Return to console</Link></Button>
          <Button asChild variant="outline"><Link href="/tools">Open tools</Link></Button>
        </div>
      </div>
    </main>
  );
}
