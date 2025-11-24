'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';

type Service = { name: string; display_name: string; status: string };

export default function ServiceManagerPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [status, setStatus] = useState<string | null>(null);

  const load = async () => {
    const res = await fetch(`${CONTROL_BASE}/api/services`, { credentials: 'include' });
    if (!res.ok) {
      setStatus('Failed to load services');
      return;
    }
    const data = await res.json();
    setServices(data.services ?? []);
  };

  useEffect(() => {
    load();
  }, []);

  const trigger = async (name: string, action: 'start' | 'stop' | 'restart') => {
    setStatus(null);
    const res = await fetch(`${CONTROL_BASE}/api/services/${name}/action`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action }),
    });
    if (!res.ok) {
      setStatus(`Action failed: ${await res.text()}`);
      return;
    }
    setStatus(`${action} command dispatched for ${name}`);
    load();
  };

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Service Manager</h2>
        <p className="text-xs text-white/60">Control core services through docker, systemd, or custom script backends.</p>
      </header>
      {status && <div className="text-xs text-white/60">{status}</div>}
      <div className="overflow-hidden rounded-2xl border border-white/10">
        <table className="min-w-full divide-y divide-white/10 text-sm">
          <thead className="bg-white/5">
            <tr>
              <th className="px-4 py-2 text-right">Service</th>
              <th className="px-4 py-2 text-right">Status</th>
              <th className="px-4 py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {services.map((service) => (
              <tr key={service.name} className="hover:bg-white/5">
                <td className="px-4 py-2 text-white/80">{service.display_name || service.name}</td>
                <td className="px-4 py-2 text-white/60">{service.status}</td>
                <td className="px-4 py-2">
                  <div className="flex flex-wrap justify-end gap-2">
                    <button
                      onClick={() => trigger(service.name, 'start')}
                      className="rounded-lg bg-emerald-500/80 px-3 py-1 text-xs text-white hover:bg-emerald-500"
                      type="button"
                    >
                      Start
                    </button>
                    <button
                      onClick={() => trigger(service.name, 'stop')}
                      className="rounded-lg bg-amber-500/60 px-3 py-1 text-xs text-white hover:bg-amber-500"
                      type="button"
                    >
                      Stop
                    </button>
                    <button
                      onClick={() => trigger(service.name, 'restart')}
                      className="rounded-lg bg-blue-500/70 px-3 py-1 text-xs text-white hover:bg-blue-500"
                      type="button"
                    >
                      Restart
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
