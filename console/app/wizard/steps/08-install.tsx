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
      const response: RunResponse = await trigger('apply.partition');
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
      <p>Disk operations require kiosk mode with root access and the AIONOS_ALLOW_INSTALL flag.</p>
      <button onClick={execute} disabled={status === 'running'}>
        Begin installation
      </button>
      <p>Status: {status}</p>
      {error && <p>{error}</p>}
    </div>
  );
}
