'use client';

import { useState } from 'react';

type RunResponse = { ok?: boolean; error?: string };

async function trigger(task: string, payload: Record<string, unknown> = {}) {
  const res = await fetch('/api/installer/run', {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ task, payload }),
  });
  return res.json();
}

export default function Install() {
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState<string | null>(null);

  const execute = async () => {
    setStatus('running');
    setError(null);
    try {
      const bootstrap: RunResponse = await trigger('bootstrap.runtime');
      if (!bootstrap?.ok) {
        throw new Error(bootstrap?.error ?? 'Failed to prepare runtime packages');
      }

      const response: RunResponse = await trigger('apply.partition', { mode: 'native' });
      if (response?.ok) {
        setStatus('done');
      } else {
        setStatus('error');
        setError(response?.error ?? 'Unknown error');
      }
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Failed to start');
    }
  };

  return (
    <div>
      <h3>Install</h3>
      <p>Installer will download missing runtime packages, run services, and then apply disk actions.</p>
      <button onClick={execute} disabled={status === 'running'}>
        Begin installation
      </button>
      <p>Status: {status}</p>
      {error && <p>{error}</p>}
    </div>
  );
}
