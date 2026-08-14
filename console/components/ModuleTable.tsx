interface ModuleRow {
  name: string;
  runtime: string;
  version: string;
  intents: string[];
  gpu?: string;
}

interface Props {
  modules: ModuleRow[];
}

export function ModuleTable({ modules }: Props) {
  return (
    <div className="overflow-hidden rounded-3xl border border-white/10 shadow-glass">
      <table className="min-w-full divide-y divide-white/10">
        <thead className="bg-white/5 text-left text-xs uppercase tracking-wide text-slate-300">
          <tr>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Runtime</th>
            <th className="px-4 py-3">Version</th>
            <th className="px-4 py-3">Intents</th>
            <th className="px-4 py-3">GPU</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5 text-sm text-slate-200">
          {modules.map((module) => (
            <tr key={module.name} className="bg-slate-900/30 hover:bg-slate-900/50">
              <td className="px-4 py-3 font-medium text-white">{module.name}</td>
              <td className="px-4 py-3">{module.runtime}</td>
              <td className="px-4 py-3">{module.version}</td>
              <td className="px-4 py-3 text-xs">{module.intents.join(', ')}</td>
              <td className="px-4 py-3">{module.gpu ?? 'CPU'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
