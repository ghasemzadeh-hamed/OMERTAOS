'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

type Stream = { name: string; path: string };

export default function LogCenterPage() {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [grep, setGrep] = useState('');
  const [lines, setLines] = useState<string[]>([]);

  useEffect(() => {
    const loadStreams = async () => {
      const res = await fetch(`${CONTROL_BASE}/api/logs/streams`, { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      setStreams(data.streams ?? []);
      if ((data.streams ?? []).length > 0) {
        setSelected(data.streams[0].name);
      }
    };
    loadStreams();
  }, []);

  useEffect(() => {
    if (!selected) return;
    const loadTail = async () => {
      const url = new URL(`${CONTROL_BASE}/api/logs/tail`);
      url.searchParams.set('stream', selected);
      url.searchParams.set('lines', '200');
      if (grep.trim()) {
        url.searchParams.set('grep', grep.trim());
      }
      const res = await fetch(url.toString(), { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      setLines(data.entries ?? []);
    };
    loadTail();
    const interval = setInterval(loadTail, 5000);
    return () => clearInterval(interval);
  }, [selected, grep]);

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Log Center</h2>
        <p className="text-xs text-white/60">Centralize live log tailing with search filters and auto-refresh.</p>
      </header>
      <div className="flex flex-col gap-3 text-sm text-white/80 md:flex-row md:items-end">
        <label className="flex-1">
          <span className="mb-1 block text-xs text-white/60">Stream</span>
          <select
            value={selected}
            onChange={(event) => setSelected(event.target.value)}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
          >
            {streams.map((stream) => (
              <option key={stream.name} value={stream.name}>
                {stream.name}
              </option>
            ))}
          </select>
        </label>
        <label className="flex-1">
          <span className="mb-1 block text-xs text-white/60">Grep</span>
          <input
            value={grep}
            onChange={(event) => setGrep(event.target.value)}
            placeholder="error"
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
          />
        </label>
      </div>
      <div className="rounded-2xl border border-white/10 bg-black/50 p-4 text-xs text-emerald-100">
        <pre className="max-h-[520px] overflow-auto leading-6">
          {lines.length ? lines.join('\n') : 'No log entries'}
        </pre>
      </div>
    </div>
  );
}
