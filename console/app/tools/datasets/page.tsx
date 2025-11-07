'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

type Dataset = { name: string; path: string; type: string; status?: string };

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [name, setName] = useState('');
  const [path, setPath] = useState('');
  const [dtype, setDtype] = useState('documents');
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/datasets`, { credentials: 'include' });
    if (!res.ok) {
      setStatus('Failed to load datasets');
      return;
    }
    const data = await res.json();
    setDatasets(data.datasets ?? []);
  };

  useEffect(() => {
    load();
  }, []);

  const register = async () => {
    if (!name.trim() || !path.trim()) {
      setStatus('Name and path required');
      return;
    }
    const res = await fetch(`${CONTROL_BASE}/api/datasets/register`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name.trim(), path: path.trim(), type: dtype }),
    });
    if (!res.ok) {
      setStatus(`Failed to register: ${await res.text()}`);
      return;
    }
    setStatus('Dataset registered');
    setName('');
    setPath('');
    load();
  };

  const remove = async (dataset: Dataset) => {
    const res = await fetch(`${CONTROL_BASE}/api/datasets/delete`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: dataset.name }),
    });
    if (!res.ok) {
      setStatus(`Failed to delete: ${await res.text()}`);
      return;
    }
    setStatus('Dataset deleted');
    load();
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Dataset Loader</h2>
        <p className="text-xs text-white/60">Register datasets for RAG pipelines or agent workflows.</p>
      </header>
      {status && <div className="text-xs text-white/60">{status}</div>}
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">Register dataset</h3>
        <div className="grid gap-3 md:grid-cols-2">
          <label className="space-y-1 text-sm text-white/70">
            <span className="text-xs text-white/60">Name</span>
            <input value={name} onChange={(event) => setName(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
          </label>
          <label className="space-y-1 text-sm text-white/70">
            <span className="text-xs text-white/60">Type</span>
            <select value={dtype} onChange={(event) => setDtype(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2">
              <option value="documents">documents</option>
              <option value="json">json</option>
              <option value="csv">csv</option>
            </select>
          </label>
          <label className="space-y-1 text-sm text-white/70 md:col-span-2">
            <span className="text-xs text-white/60">Path or URL</span>
            <input value={path} onChange={(event) => setPath(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
          </label>
        </div>
        <button onClick={register} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500" type="button">
          Register
        </button>
      </section>
      <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">Datasets</h3>
        <div className="overflow-hidden rounded-xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-sm">
            <thead className="bg-white/5">
              <tr>
                <th className="px-4 py-2 text-right">Name</th>
                <th className="px-4 py-2 text-right">Type</th>
                <th className="px-4 py-2 text-right">Status</th>
                <th className="px-4 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {datasets.map((dataset) => (
                <tr key={dataset.name} className="hover:bg-white/5">
                  <td className="px-4 py-2 text-white/80">{dataset.name}</td>
                  <td className="px-4 py-2 text-white/60">{dataset.type}</td>
                  <td className="px-4 py-2 text-white/60">{dataset.status ?? 'registered'}</td>
                  <td className="px-4 py-2 text-right">
                    <button onClick={() => remove(dataset)} className="rounded-lg bg-red-500/70 px-3 py-1 text-xs text-white hover:bg-red-500" type="button">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
