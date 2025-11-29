'use client';

import { useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';

type CsvPreview = {
  type: 'csv';
  columns: string[];
  rows: string[][];
};

type JsonPreview = {
  type: 'json';
  content: any;
  top_level_keys: string[];
};

type PreviewResponse = (CsvPreview | JsonPreview | { unsupported_type: boolean }) & { path: string };

export default function DataStudioPage() {
  const [path, setPath] = useState('');
  const [limit, setLimit] = useState(100);
  const [preview, setPreview] = useState<PreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPreview = async () => {
    if (!path.trim()) {
      window.alert('Enter a file path');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const url = new URL(`${CONTROL_BASE}/api/data/preview`);
      url.searchParams.set('path', path.trim());
      url.searchParams.set('limit', limit.toString());
      const res = await fetch(url.toString(), { credentials: 'include' });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setPreview(await res.json());
    } catch (err) {
      setError((err as Error).message);
      setPreview(null);
    } finally {
      setLoading(false);
    }
  };

  const unsupportedPreview =
    preview && 'unsupported_type' in preview ? preview.unsupported_type : false;
  const csvPreview =
    preview && 'type' in preview && preview.type === 'csv' ? preview : null;
  const jsonPreview =
    preview && 'type' in preview && preview.type === 'json' ? preview : null;

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">AION Data Studio</h2>
        <p className="text-xs text-white/60">Preview CSV and JSON datasets to troubleshoot agent pipelines.</p>
      </header>
      <div className="flex flex-col gap-3 text-sm text-white/80 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="mb-1 block text-xs text-white/60">File path</span>
          <input
            value={path}
            onChange={(event) => setPath(event.target.value)}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 outline-none focus:border-emerald-400"
            placeholder="/models/sample.csv"
          />
        </label>
        <label>
          <span className="mb-1 block text-xs text-white/60">Limit</span>
          <input
            type="number"
            min={1}
            max={1000}
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
            className="w-24 rounded-xl border border-white/10 bg-white/5 px-3 py-2"
          />
        </label>
        <button
          onClick={loadPreview}
          className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500"
          disabled={loading}
          type="button"
        >
          {loading ? 'Loading...' : 'Load'}
        </button>
      </div>
      {error && <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-200">{error}</div>}
      {unsupportedPreview && (
        <div className="rounded-xl border border-yellow-400/30 bg-yellow-400/10 p-3 text-sm text-yellow-200">
          Unsupported file type. Only CSV and JSON are currently supported.
        </div>
      )}
      {csvPreview && (
        <div className="overflow-auto rounded-2xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-xs">
            <thead className="bg-white/5">
              <tr>
                {csvPreview.columns.map((col) => (
                  <th key={col} className="px-3 py-2 text-right font-medium">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {csvPreview.rows.map((row, idx) => (
                <tr key={idx} className="hover:bg-white/5">
                  {row.map((cell, i) => (
                    <td key={`${idx}-${i}`} className="px-3 py-2 text-white/70">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {jsonPreview && (
        <div className="space-y-2">
          <div className="text-xs text-white/60">Top level keys: {jsonPreview.top_level_keys.join(', ') || '-'}</div>
          <pre className="max-h-[420px] overflow-auto rounded-2xl border border-white/10 bg-black/40 p-4 text-xs text-emerald-100">
            {JSON.stringify(jsonPreview.content, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
