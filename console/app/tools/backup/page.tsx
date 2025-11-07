'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

type BackupEntry = { created_at: string; path: string };

export default function BackupPage() {
  const [history, setHistory] = useState<BackupEntry[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/backup/history`, { credentials: 'include' });
    if (!res.ok) return;
    const data = await res.json();
    setHistory(data.history ?? []);
  };

  useEffect(() => {
    load();
  }, []);

  const run = async () => {
    setStatus('');
    const res = await fetch(`${CONTROL_BASE}/api/backup/run`, {
      method: 'POST',
      credentials: 'include',
    });
    if (!res.ok) {
      setStatus(`Backup failed: ${await res.text()}`);
      return;
    }
    setStatus('Backup started');
    load();
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Backup &amp; Snapshot</h2>
        <p className="text-xs text-white/60">Trigger backups of configuration, databases, and model metadata.</p>
      </header>
      <button onClick={run} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500" type="button">
        Run backup now
      </button>
      {status && <div className="text-xs text-white/60">{status}</div>}
      <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <h3 className="text-lg font-semibold text-white/85">History</h3>
        <ul className="space-y-2 text-sm text-white/80">
          {history.map((entry) => (
            <li key={entry.created_at} className="rounded-xl border border-white/10 bg-black/40 p-3">
              <div>{new Date(entry.created_at).toLocaleString()}</div>
              <div className="text-xs text-emerald-200">{entry.path}</div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
