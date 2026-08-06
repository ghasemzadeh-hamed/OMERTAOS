import { ExternalLink, Search } from 'lucide-react';
import { useDeferredValue, useEffect, useRef, useState } from 'react';
import { openUrl } from '@tauri-apps/plugin-opener';
import { isTauri } from '@tauri-apps/api/core';
import { SHELL_APPS } from '../lib/apps';
import { readSettings } from '../lib/config';
import { useShellStore } from '../lib/shellStore';

export function CommandPalette() {
  const [query, setQuery] = useState('');
  const deferredQuery = useDeferredValue(query.toLowerCase());
  const inputRef = useRef<HTMLInputElement>(null);
  const openApp = useShellStore((state) => state.openApp);
  const setPaletteOpen = useShellStore((state) => state.setPaletteOpen);
  const appCommands = SHELL_APPS.filter((app) => app.label.toLowerCase().includes(deferredQuery));
  const showWeb = 'open web console'.includes(deferredQuery);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const openWebConsole = async () => {
    const url = readSettings().consoleUrl;
    try { await openUrl(url); } catch { if (!isTauri()) window.open(url, '_blank', 'noopener,noreferrer'); }
    setPaletteOpen(false);
  };

  return (
    <div className="palette-backdrop" onMouseDown={() => setPaletteOpen(false)}>
      <section className="command-palette panel" onMouseDown={(event) => event.stopPropagation()} aria-label="Command palette">
        <label className="palette-search"><Search size={18} /><input ref={inputRef} value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Type a command or search…" /><kbd>Esc</kbd></label>
        <div className="command-list">
          {appCommands.map(({ id, label, icon: Icon }, index) => <button className={index === 0 ? 'selected' : ''} onClick={() => openApp(id)} key={id}><Icon size={18} /><span>Open {label}</span><kbd>↵</kbd></button>)}
          {showWeb ? <button onClick={() => void openWebConsole()}><ExternalLink size={18} /><span>Open Web Console</span><kbd>↗</kbd></button> : null}
        </div>
      </section>
    </div>
  );
}
