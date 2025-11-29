'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';

type NetworkConfig = {
  api_base_url?: string;
  gateway_url?: string;
  console_url?: string;
  minio_endpoint?: string;
  qdrant_endpoint?: string;
  tls_cert_path?: string;
  tls_key_path?: string;
};

export default function NetworkConfigPage() {
  const [form, setForm] = useState<NetworkConfig>({});
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`${CONTROL_BASE}/api/network/config`, { credentials: 'include' });
      if (!res.ok) {
        setStatus('Failed to load network config');
        return;
      }
      const data = await res.json();
      setForm(data.network ?? {});
    };
    load();
  }, []);

  const updateField = (key: keyof NetworkConfig, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const save = async () => {
    setStatus(null);
    const res = await fetch(`${CONTROL_BASE}/api/network/config`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    if (!res.ok) {
      setStatus(`Failed to save: ${await res.text()}`);
      return;
    }
    setStatus('Network configuration updated');
  };

  const ping = async (url?: string) => {
    if (!url) {
      setStatus('Set a URL before running ping');
      return;
    }
    try {
      const response = await fetch(url, { method: 'HEAD' });
      setStatus(`Ping ${url}: ${response.status}`);
    } catch (err) {
      setStatus(`Ping failed: ${(err as Error).message}`);
    }
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Network Configurator</h2>
        <p className="text-xs text-white/60">Tune service endpoints and TLS certificate paths from one screen.</p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="block space-y-1 text-sm text-white/70">
          <span className="text-xs text-white/60">API base URL</span>
          <input value={form.api_base_url ?? ''} onChange={(event) => updateField('api_base_url', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <label className="block space-y-1 text-sm text-white/70">
          <span className="text-xs text-white/60">Gateway URL</span>
          <input value={form.gateway_url ?? ''} onChange={(event) => updateField('gateway_url', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <label className="block space-y-1 text-sm text-white/70">
          <span className="text-xs text-white/60">Console URL</span>
          <input value={form.console_url ?? ''} onChange={(event) => updateField('console_url', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <label className="block space-y-1 text-sm text-white/70">
          <span className="text-xs text-white/60">MinIO endpoint</span>
          <input value={form.minio_endpoint ?? ''} onChange={(event) => updateField('minio_endpoint', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <label className="block space-y-1 text-sm text-white/70">
          <span className="text-xs text-white/60">Qdrant endpoint</span>
          <input value={form.qdrant_endpoint ?? ''} onChange={(event) => updateField('qdrant_endpoint', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </label>
        <div className="space-y-1">
          <span className="text-xs text-white/60">TLS certificate</span>
          <input value={form.tls_cert_path ?? ''} onChange={(event) => updateField('tls_cert_path', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
          <span className="text-xs text-white/60">TLS key</span>
          <input value={form.tls_key_path ?? ''} onChange={(event) => updateField('tls_key_path', event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2" />
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <button onClick={save} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500" type="button">
          Save
        </button>
        <button onClick={() => ping(form.gateway_url)} className="rounded-xl bg-white/10 px-4 py-2 text-sm hover:bg-white/20" type="button">
          Ping gateway
        </button>
        <button onClick={() => ping(form.api_base_url)} className="rounded-xl bg-white/10 px-4 py-2 text-sm hover:bg-white/20" type="button">
          Ping API
        </button>
      </div>
      {status && <div className="text-xs text-white/60">{status}</div>}
    </div>
  );
}
