import type { PropsWithChildren } from 'react';

export function GlassCard({ children, className = '' }: PropsWithChildren<{ className?: string }>) {
  return <div className={`glass glass-accent p-6 ${className}`.trim()}>{children}</div>;
}

export default GlassCard;
