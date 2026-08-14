export interface PipelineRun {
  name: string;
  branch: string;
  status: 'success' | 'running' | 'failed';
  duration: string;
  triggeredBy: string;
}

const statusCopy: Record<PipelineRun['status'], string> = {
  success: 'Passed',
  running: 'Running',
  failed: 'Failed',
};

const statusStyles: Record<PipelineRun['status'], string> = {
  success: 'bg-emerald-500/20 text-emerald-200 border-emerald-500/40',
  running: 'bg-sky-500/20 text-sky-200 border-sky-500/40 animate-pulse',
  failed: 'bg-rose-500/20 text-rose-200 border-rose-500/40',
};

export function PipelinePanel({ runs }: { runs: PipelineRun[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-white/10 bg-slate-900/60">
      <table className="min-w-full divide-y divide-white/10">
        <thead className="bg-white/5 text-left text-xs uppercase tracking-wide text-slate-300">
          <tr>
            <th className="px-4 py-3 font-semibold">Pipeline</th>
            <th className="px-4 py-3 font-semibold">Branch</th>
            <th className="px-4 py-3 font-semibold">Status</th>
            <th className="px-4 py-3 font-semibold">Duration</th>
            <th className="px-4 py-3 font-semibold">Triggered by</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5 text-sm text-slate-200">
          {runs.map((run) => (
            <tr key={`${run.name}-${run.branch}`}>
              <td className="px-4 py-3 font-medium text-white">{run.name}</td>
              <td className="px-4 py-3 font-mono text-xs text-slate-300">{run.branch}</td>
              <td className="px-4 py-3">
                <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${statusStyles[run.status]}`}>
                  {statusCopy[run.status]}
                </span>
              </td>
              <td className="px-4 py-3 text-xs text-slate-300">{run.duration}</td>
              <td className="px-4 py-3 text-xs text-slate-300">{run.triggeredBy}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
