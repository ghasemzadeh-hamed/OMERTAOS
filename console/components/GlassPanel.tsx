import { ReactNode } from 'react';
import { twMerge } from 'tailwind-merge';

interface GlassPanelProps {
  className?: string;
  children: ReactNode;
}

export default function GlassPanel({ className, children }: GlassPanelProps) {
  return (
    <div
      className={twMerge(
        'glass relative overflow-hidden rounded-2xl border border-white/15 bg-white/10 text-white/80 backdrop-blur-lg backdrop-saturate-150',
        className,
      )}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 rounded-2xl"
        style={{
          maskImage: 'linear-gradient(#000, rgba(0,0,0,0.35) 65%, transparent 85%)',
          WebkitMaskImage: 'linear-gradient(#000, rgba(0,0,0,0.35) 65%, transparent 85%)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
