export type InstallerStatus = 'pending' | 'running' | 'success' | 'error';

export interface InstallerStep {
  title: string;
  description: string;
  status: InstallerStatus;
  duration?: string;
}

const statusLabel: Record<InstallerStatus, string> = {
  pending: 'Pending',
  running: 'Running',
  success: 'Completed',
  error: 'Failed',
};

const statusStyles: Record<InstallerStatus, string> = {
  pending: 'bg-yellow-500/20 text-yellow-200 border-yellow-500/40',
  running: 'bg-sky-500/20 text-sky-200 border-sky-500/40 animate-pulse',
  success: 'bg-emerald-500/20 text-emerald-200 border-emerald-500/40',
  error: 'bg-rose-500/20 text-rose-200 border-rose-500/40',
};

export function InstallerPanel({ steps }: { steps: InstallerStep[] }) {
  return (
    <ol className="space-y-4">
      {steps.map((step, index) => (
        <li key={step.title} className="flex items-start gap-4">
          <div className="relative flex flex-col items-center">
            <span className="flex h-8 w-8 items-center justify-center rounded-full border border-white/20 bg-white/5 text-sm font-semibold text-white">
              {index + 1}
            </span>
            {index < steps.length - 1 ? <span className="mt-1 h-full w-px bg-white/10" aria-hidden /> : null}
          </div>
          <div className="flex-1 rounded-xl border border-white/10 bg-slate-900/60 p-4 shadow-inner">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="text-sm font-semibold text-white">{step.title}</h3>
              <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${statusStyles[step.status]}`}>
                {statusLabel[step.status]}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-300">{step.description}</p>
            {step.duration ? (
              <p className="mt-2 text-xs uppercase tracking-wide text-slate-400">{step.duration}</p>
            ) : null}
          </div>
        </li>
      ))}
    </ol>
  );
}
