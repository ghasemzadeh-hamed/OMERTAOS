import { useCallback, useEffect, useState } from 'react';
import { Activity, RefreshCw } from 'lucide-react';
import { checkService, getGatewayHealth } from '../lib/gatewayClient';
import { readSettings } from '../lib/config';
import type { ServiceState } from '../types/shell';

interface HealthItem { label: string; detail: string; state: ServiceState }

export function SystemMonitorApp() {
  const [services, setServices] = useState<HealthItem[]>([
    { label: 'Console', detail: 'HTTP /', state: 'checking' },
    { label: 'Gateway', detail: 'GET /health', state: 'checking' },
    { label: 'Control', detail: 'GET /health', state: 'checking' },
    { label: 'Runtime', detail: 'Capability endpoint unavailable', state: 'offline' },
  ]);

  const refresh = useCallback(async () => {
    const { consoleUrl } = readSettings();
    setServices((current) => current.map((item) => item.label === 'Runtime' ? item : { ...item, state: 'checking' }));
    const [consoleState, gatewayHealth] = await Promise.all([
      checkService(consoleUrl),
      getGatewayHealth(),
    ]);
    setServices([
      { label: 'Console', detail: 'HTTP /', state: consoleState },
      { label: 'Gateway', detail: 'GET /health', state: gatewayHealth.state },
      { label: 'Control', detail: 'Reported by Gateway /health', state: gatewayHealth.controlState },
      { label: 'Runtime', detail: 'Capability endpoint unavailable', state: 'offline' },
    ]);
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  return (
    <div className="app-page monitor-app">
      <header className="app-heading"><div><span className="section-label">Health</span><h2>System Monitor</h2></div><button className="button button-secondary" onClick={() => void refresh()}><RefreshCw size={15} />Refresh</button></header>
      <div className="health-grid">
        {services.map((service) => (
          <article className="health-card" key={service.label}>
            <div className={`health-indicator ${service.state}`}><Activity size={19} /></div>
            <div><h3>{service.label}</h3><p>{service.detail}</p></div>
            <strong className={`health-state ${service.state}`}>{service.state}</strong>
          </article>
        ))}
      </div>
      <div className="monitor-note">Health checks are read-only. No service control or privileged runtime access is exposed by the Desktop Shell.</div>
    </div>
  );
}
