import { Search, X } from 'lucide-react';
import { useDeferredValue, useEffect, useRef, useState } from 'react';
import { SHELL_APPS } from '../lib/apps';
import { useShellStore } from '../lib/shellStore';

export function AppLauncher() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query.trim().toLowerCase());
  const inputRef = useRef<HTMLInputElement>(null);
  const openApp = useShellStore((state) => state.openApp);
  const setLauncherOpen = useShellStore((state) => state.setLauncherOpen);
  const apps = deferredQuery
    ? SHELL_APPS.filter((app) => `${app.label} ${app.description}`.toLowerCase().includes(deferredQuery))
    : SHELL_APPS;

  useEffect(() => { inputRef.current?.focus(); }, []);

  return (
    <aside className="launcher panel" aria-label="Application launcher">
      <div className="panel-heading"><strong>Applications</strong><button className="icon-button" onClick={() => setLauncherOpen(false)} aria-label="Close launcher"><X size={17} /></button></div>
      <label className="search-field"><Search size={16} /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search apps" /></label>
      <div className="launcher-grid">
        {apps.map(({ id, label, description, icon: Icon }) => <button onClick={() => openApp(id)} key={id}><Icon size={22} /><span><strong>{label}</strong><small>{description}</small></span></button>)}
      </div>
      {apps.length === 0 ? <p className="empty-search">No applications found.</p> : null}
    </aside>
  );
}
