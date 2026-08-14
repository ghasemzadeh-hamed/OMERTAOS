'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';
const PROM_URL = process.env.NEXT_PUBLIC_PROM_URL;

export default function MetricsIntegrationPage() {
  const [system, setSystem] = useState<any>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`${CONTROL_BASE}/api/metrics/system`, { credentials: 'include' });
      if (!res.ok) return;
      setSystem(await res.json());
    };
    load();
  }, []);

  return (
    <div className="space-y-4 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Metrics Dashboard</h2>
        <p className="text-xs text-white/60">Embed Prometheus or Grafana dashboards, or fall back to local summaries.</p>
      </header>
      {PROM_URL ? (
        <div className="rounded-2xl border border-white/10 bg-black/40 p-2">
          <iframe src={PROM_URL} title="Metrics" className="h-[420px] w-full rounded-xl border-0" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          {system && (
            <>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <h3 className="text-sm font-semibold text-white/80">CPU</h3>
                <p className="text-lg font-semibold text-white/90">{system.cpu.percent.toFixed(1)}%</p>
                <p className="text-xs text-white/60">Cores: {system.cpu.cores}</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <h3 className="text-sm font-semibold text-white/80">Memory</h3>
                <p className="text-lg font-semibold text-white/90">{system.memory.percent.toFixed(1)}%</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <h3 className="text-sm font-semibold text-white/80">Disk</h3>
                <p className="text-lg font-semibold text-white/90">{system.disk.percent.toFixed(1)}%</p>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
