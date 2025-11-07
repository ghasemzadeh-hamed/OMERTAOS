'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

export default function UpdateCenterPage() {
  const [current, setCurrent] = useState('');
  const [latest, setLatest] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/update/status`, { credentials: 'include' });
    if (!res.ok) return;
    const data = await res.json();
    setCurrent(data.current ?? '');
  };

  useEffect(() => {
    load();
  }, []);

  const check = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/update/check`, { method: 'POST', credentials: 'include' });
    if (!res.ok) {
      setStatus(`Check failed: ${await res.text()}`);
      return;
    }
    const data = await res.json();
    setLatest(data.latest ?? null);
    setStatus(data.notes ?? 'Checked update feed');
  };

  const apply = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/update/apply`, { method: 'POST', credentials: 'include' });
    if (!res.ok) {
      setStatus(`Update failed: ${await res.text()}`);
      return;
    }
    setStatus('Update script executed');
    load();
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Update Center</h2>
        <p className="text-xs text-white/60">Check for new releases and run the configured update scripts.</p>
      </header>
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
        <p>Current version: {current || 'unknown'}</p>
        <p>Latest available: {latest ?? 'unknown'}</p>
      </div>
      <div className="flex gap-3">
        <button onClick={check} className="rounded-xl bg-white/10 px-4 py-2 text-sm hover:bg-white/20" type="button">
          Check updates
        </button>
        <button onClick={apply} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500" type="button">
          Apply update
        </button>
      </div>
      {status && <div className="text-xs text-white/60">{status}</div>}
    </div>
  );
}
