import { Grid2X2 } from 'lucide-react';
import { SHELL_APPS } from '../lib/apps';
import { useShellStore } from '../lib/shellStore';

export function Dock() {
  const windows = useShellStore((state) => state.windows);
  const openApp = useShellStore((state) => state.openApp);
  const launcherOpen = useShellStore((state) => state.launcherOpen);
  const setLauncherOpen = useShellStore((state) => state.setLauncherOpen);

  return (
    <nav className="dock" aria-label="Applications">
      <button className={`dock-item launcher-button ${launcherOpen ? 'active' : ''}`} onClick={() => setLauncherOpen(!launcherOpen)} title="Applications">
        <Grid2X2 size={22} /><span>Apps</span>
      </button>
      <span className="dock-divider" />
      {SHELL_APPS.map(({ id, label, icon: Icon }) => {
        const windowState = windows.find((item) => item.appId === id);
        return (
          <button className={`dock-item ${windowState && !windowState.minimized ? 'active' : ''}`} onClick={() => openApp(id)} key={id} title={label}>
            <Icon size={22} /><span>{label}</span>{windowState ? <i /> : null}
          </button>
        );
      })}
    </nav>
  );
}
