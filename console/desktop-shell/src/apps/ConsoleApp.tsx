import { useState } from 'react';
import { ExternalLink, Globe2, RefreshCw } from 'lucide-react';
import { openUrl } from '@tauri-apps/plugin-opener';
import { isTauri } from '@tauri-apps/api/core';
import { readSettings } from '../lib/config';

async function openExternal(url: string) {
  try {
    await openUrl(url);
  } catch {
    if (!isTauri()) window.open(url, '_blank', 'noopener,noreferrer');
  }
}

export function ConsoleApp() {
  const { consoleUrl } = readSettings();
  const [embedReady, setEmbedReady] = useState(false);
  const [embedKey, setEmbedKey] = useState(0);

  return (
    <div className="console-app app-surface">
      <div className="browser-bar">
        <Globe2 size={16} aria-hidden="true" />
        <div className="address-field">{consoleUrl}</div>
        <button className="icon-button" onClick={() => { setEmbedReady(false); setEmbedKey((key) => key + 1); }} aria-label="Reload Web Console">
          <RefreshCw size={16} />
        </button>
        <button className="button button-secondary" onClick={() => openExternal(consoleUrl)}>
          Open in browser <ExternalLink size={15} />
        </button>
      </div>
      <div className="console-embed">
        <iframe className={embedReady ? 'ready' : ''} key={embedKey} title="OMERTAOS Web Console" src={consoleUrl} onLoad={() => setEmbedReady(true)} />
        <div className={`embed-fallback ${embedReady ? 'hidden' : ''}`}>
          <div className="console-mark"><Globe2 size={38} /></div>
          <h2>Web Console</h2>
          <p>The existing OMERTAOS Console is available as an embedded workspace or in your browser.</p>
          <button className="button button-primary" onClick={() => openExternal(consoleUrl)}>
            Open in browser <ExternalLink size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
