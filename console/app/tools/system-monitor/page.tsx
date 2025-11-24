'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';

type SystemMetrics = {
  cpu: { percent: number; cores: number };
  memory: { total: any; used: any; percent: number };
  disk: { path: string; total: any; used: any; percent: number };
  gpu: Array<{ id: number; name: string; utilization: number; memory_total_mb: number; memory_used_mb: number }>;
};

type ServiceStatus = { name: string; url: string; status: string };

type AgentMetrics = { running_agents: number; queued_tasks: number; recent_jobs: Array<{ event_id: string; status: string; detail: string }> };

export default function SystemMonitorPage() {
  const [system, setSystem] = useState<SystemMetrics | null>(null);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [agents, setAgents] = useState<AgentMetrics | null>(null);

  const load = async () => {
    const [sysRes, svcRes, agentRes] = await Promise.all([
      fetch(`${CONTROL_BASE}/api/metrics/system`, { credentials: 'include' }),
      fetch(`${CONTROL_BASE}/api/metrics/services`, { credentials: 'include' }),
      fetch(`${CONTROL_BASE}/api/metrics/agents`, { credentials: 'include' }),
    ]);
    if (sysRes.ok) setSystem(await sysRes.json());
    if (svcRes.ok) {
      const data = await svcRes.json();
      setServices(data.services ?? []);
    }
    if (agentRes.ok) setAgents(await agentRes.json());
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-5 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">System Monitor</h2>
        <p className="text-xs text-white/60">View resource usage, service health, and agent queues in near real time.</p>
      </header>
      {system && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-sm font-semibold text-white/80">CPU</h3>
            <p className="text-lg font-semibold text-white/90">{system.cpu.percent.toFixed(1)}%</p>
            <p className="text-xs text-white/60">Cores: {system.cpu.cores}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-sm font-semibold text-white/80">Memory</h3>
            <p className="text-lg font-semibold text-white/90">{system.memory.percent.toFixed(1)}%</p>
            <p className="text-xs text-white/60">Used: {system.memory.used.gb} GB / {system.memory.total.gb} GB</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-sm font-semibold text-white/80">Disk ({system.disk.path})</h3>
            <p className="text-lg font-semibold text-white/90">{system.disk.percent.toFixed(1)}%</p>
            <p className="text-xs text-white/60">Used: {system.disk.used.gb} GB / {system.disk.total.gb} GB</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <h3 className="text-sm font-semibold text-white/80">GPU</h3>
            {system.gpu.length === 0 ? (
              <p className="text-xs text-white/60">No GPU detected.</p>
            ) : (
              <ul className="space-y-1 text-xs text-white/70">
                {system.gpu.map((gpu) => (
                  <li key={gpu.id}>
                    {gpu.name} &mdash; {gpu.utilization.toFixed(1)}% / {gpu.memory_used_mb}MB
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
      <section className="space-y-3">
        <h3 className="text-lg font-semibold text-white/85">Service status</h3>
        <div className="overflow-hidden rounded-2xl border border-white/10">
          <table className="min-w-full divide-y divide-white/10 text-sm">
            <thead className="bg-white/5">
              <tr>
                <th className="px-4 py-2 text-right">Service</th>
                <th className="px-4 py-2 text-right">Health URL</th>
                <th className="px-4 py-2 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {services.map((service) => (
                <tr key={service.name} className="hover:bg-white/5">
                  <td className="px-4 py-2 text-white/80">{service.name}</td>
                  <td className="px-4 py-2 text-xs text-emerald-200">{service.url}</td>
                  <td className="px-4 py-2 text-white/70">{service.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {agents && (
        <section className="space-y-3">
          <h3 className="text-lg font-semibold text-white/85">Agents</h3>
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
            <p>Running agents: {agents.running_agents}</p>
            <p>Queued tasks: {agents.queued_tasks}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-black/40 p-4 text-xs text-emerald-100">
            <h4 className="mb-2 text-sm font-semibold text-white/80">Recent jobs</h4>
            <pre className="max-h-60 overflow-auto">{JSON.stringify(agents.recent_jobs, null, 2)}</pre>
          </div>
        </section>
      )}
    </div>
  );
}
