'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

type ModelEntry = { name: string; path: string; size: number };
type RegistryEntry = { name: string; url?: string; installed?: boolean; description?: string };

export default function ModelsPage() {
  const [local, setLocal] = useState<ModelEntry[]>([]);
  const [registry, setRegistry] = useState<RegistryEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/models`, { credentials: 'include' });
    if (!res.ok) {
      setStatus('Failed to load models');
      return;
    }
    const data = await res.json();
    setLocal(data.local ?? []);
    setRegistry(data.registry ?? []);
  };

  useEffect(() => {
    load();
  }, []);

  const install = async (entry: RegistryEntry) => {
    const res = await fetch(`${CONTROL_BASE}/api/models/install`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: entry.name, source: 'registry' }),
    });
    if (!res.ok) {
      setStatus(`Install failed: ${await res.text()}`);
      return;
    }
    setStatus(`Install triggered for ${entry.name}`);
    load();
  };

  const remove = async (entry: ModelEntry) => {
    const res = await fetch(`${CONTROL_BASE}/api/models/remove`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: entry.name }),
    });
    if (!res.ok) {
      setStatus(`Remove failed: ${await res.text()}`);
      return;
    }
    setStatus(`Removed ${entry.name}`);
    load();
  };

  return (
    <div className="space-y-5 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Model Installer</h2>
        <p className="text-xs text-white/60">Manage local model assets and registry-sourced deployments.</p>
      </header>
      {status && <div className="text-xs text-white/60">{status}</div>}
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">Local models</h3>
        <div className="overflow-hidden rounded-xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-sm">
            <thead className="bg-white/5">
              <tr>
                <th className="px-4 py-2 text-right">Name</th>
                <th className="px-4 py-2 text-right">Size</th>
                <th className="px-4 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {local.map((model) => (
                <tr key={model.path} className="hover:bg-white/5">
                  <td className="px-4 py-2 text-white/80">{model.name}</td>
                  <td className="px-4 py-2 text-white/60">{(model.size / (1024 * 1024)).toFixed(2)} MB</td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => remove(model)} className="rounded-lg bg-red-500/70 px-3 py-1 text-xs text-white hover:bg-red-500" type="button">
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">Registry</h3>
        <div className="grid gap-3 md:grid-cols-2">
          {registry.map((entry) => (
            <div key={entry.name} className="rounded-xl border border-white/10 bg-black/40 p-4 text-sm text-white/80">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-white/90">{entry.name}</h4>
                  <p className="text-xs text-white/60">{entry.description ?? entry.url}</p>
                </div>
                <button
                  onClick={() => install(entry)}
                  disabled={entry.installed}
                  className="rounded-xl bg-emerald-500/80 px-3 py-1 text-xs text-white hover:bg-emerald-500 disabled:opacity-40"
                  type="button"
                >
                  {entry.installed ? 'Installed' : 'Install'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
