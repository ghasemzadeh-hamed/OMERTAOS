import { ReactNode } from 'react';

interface Props {
  title: string;
  description?: string;
  action?: ReactNode;
  children?: ReactNode;
}

export function GlassCard({ title, description, action, children }: Props) {
  return (
    <section className="glass-card p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">{title}</h3>
          {description ? <p className="mt-1 text-sm text-slate-300">{description}</p> : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      {children ? <div className="mt-4 space-y-4">{children}</div> : null}
    </section>
  );
}
