import { useState } from 'react';
import { Check, Link2, MonitorCog, Moon } from 'lucide-react';
import { readSettings, writeSettings } from '../lib/config';
import type { DesktopSettings, RuntimeMode } from '../types/shell';

const modes: RuntimeMode[] = ['Local', 'WSL', 'Linux', 'Bare Metal'];

export function SettingsApp() {
  const [settings, setSettings] = useState<DesktopSettings>(() => readSettings());
  const [saved, setSaved] = useState(false);

  const update = <K extends keyof DesktopSettings>(key: K, value: DesktopSettings[K]) => {
    setSettings((current) => ({ ...current, [key]: value }));
    setSaved(false);
  };

  const save = () => {
    writeSettings(settings);
    setSaved(true);
    window.dispatchEvent(new CustomEvent('omerta-settings-change'));
  };

  return (
    <div className="settings-app app-page">
      <header className="app-heading">
        <div><span className="section-label">Desktop</span><h2>Settings</h2></div>
        <button className="button button-primary" onClick={save}>{saved ? <Check size={15} /> : null}{saved ? 'Saved' : 'Save changes'}</button>
      </header>
      <section className="settings-section">
        <div className="settings-title"><Link2 size={19} /><div><h3>Connection</h3><p>Local service endpoints used by this shell.</p></div></div>
        <div className="field-grid">
          <label>Console URL<input value={settings.consoleUrl} onChange={(event) => update('consoleUrl', event.target.value)} /></label>
          <label>Gateway URL<input value={settings.gatewayUrl} onChange={(event) => update('gatewayUrl', event.target.value)} /></label>
          <label>Control URL<input value={settings.controlUrl} onChange={(event) => update('controlUrl', event.target.value)} /></label>
        </div>
      </section>
      <section className="settings-section">
        <div className="settings-title"><MonitorCog size={19} /><div><h3>Runtime Mode</h3><p>Describes where OMERTAOS is operating.</p></div></div>
        <div className="segmented-control">
          {modes.map((mode) => <button className={settings.runtimeMode === mode ? 'active' : ''} onClick={() => update('runtimeMode', mode)} key={mode}>{mode}</button>)}
        </div>
      </section>
      <section className="settings-section settings-inline">
        <div className="settings-title"><Moon size={19} /><div><h3>Appearance</h3><p>Dark mode is the native shell theme.</p></div></div>
        <label className="toggle"><input type="checkbox" checked={settings.compactMode} onChange={(event) => update('compactMode', event.target.checked)} /><span />Compact mode</label>
      </section>
    </div>
  );
}
