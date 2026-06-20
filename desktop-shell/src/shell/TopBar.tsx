import { useEffect, useState } from 'react';
import { ChevronDown, Clock3, Hexagon, Wifi, WifiOff } from 'lucide-react';
import { getGatewayHealth, type GatewayHealth } from '../lib/gatewayClient';
import { readSettings } from '../lib/config';
import type { RuntimeMode } from '../types/shell';

export function TopBar() {
  const [time, setTime] = useState(() => new Date());
  const [mode, setMode] = useState<RuntimeMode>(() => readSettings().runtimeMode);
  const [health, setHealth] = useState<GatewayHealth>({ state: 'checking', label: 'Checking Gateway' });

  useEffect(() => {
    const clock = window.setInterval(() => setTime(new Date()), 1000);
    const check = () => { void getGatewayHealth().then(setHealth); };
    const settingsChange = () => { setMode(readSettings().runtimeMode); check(); };
    check();
    const healthTimer = window.setInterval(check, 15000);
    window.addEventListener('omerta-settings-change', settingsChange);
    return () => {
      window.clearInterval(clock);
      window.clearInterval(healthTimer);
      window.removeEventListener('omerta-settings-change', settingsChange);
    };
  }, []);

  return (
    <header className="top-bar">
      <div className="brand"><span className="brand-mark"><Hexagon size={19} /></span><strong>OMERTAOS</strong></div>
      <div className="top-status">
        <button className="mode-button" aria-label={`Runtime mode: ${mode}`}>{mode}<ChevronDown size={14} /></button>
        <div className={`connection ${health.state}`} title="Gateway health">
          {health.state === 'online' ? <Wifi size={15} /> : <WifiOff size={15} />}{health.label}
        </div>
        <time dateTime={time.toISOString()}><Clock3 size={15} />{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time>
      </div>
    </header>
  );
}
