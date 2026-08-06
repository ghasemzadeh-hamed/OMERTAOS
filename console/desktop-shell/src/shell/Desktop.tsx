import { useEffect } from 'react';
import { AgentCenterApp } from '../apps/AgentCenterApp';
import { ConsoleApp } from '../apps/ConsoleApp';
import { FileManagerApp } from '../apps/FileManagerApp';
import { ModelsApp } from '../apps/ModelsApp';
import { ServicesApp } from '../apps/ServicesApp';
import { SettingsApp } from '../apps/SettingsApp';
import { SystemMonitorApp } from '../apps/SystemMonitorApp';
import { TerminalApp } from '../apps/TerminalApp';
import { useShellStore } from '../lib/shellStore';
import type { AppId } from '../types/shell';
import { AppLauncher } from './AppLauncher';
import { CommandPalette } from './CommandPalette';
import { Dock } from './Dock';
import { TopBar } from './TopBar';
import { WindowFrame } from './WindowFrame';

const APP_CONTENT: Record<AppId, () => JSX.Element> = {
  console: ConsoleApp,
  agents: AgentCenterApp,
  terminal: TerminalApp,
  files: FileManagerApp,
  models: ModelsApp,
  services: ServicesApp,
  monitor: SystemMonitorApp,
  settings: SettingsApp,
};

export function Desktop() {
  const windows = useShellStore((state) => state.windows);
  const launcherOpen = useShellStore((state) => state.launcherOpen);
  const paletteOpen = useShellStore((state) => state.paletteOpen);
  const setLauncherOpen = useShellStore((state) => state.setLauncherOpen);
  const setPaletteOpen = useShellStore((state) => state.setPaletteOpen);

  useEffect(() => {
    const keyboard = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setPaletteOpen(!useShellStore.getState().paletteOpen);
      }
      if ((event.ctrlKey || event.metaKey) && event.code === 'Space') {
        event.preventDefault();
        setLauncherOpen(!useShellStore.getState().launcherOpen);
      }
      if (event.key === 'Escape') {
        setLauncherOpen(false);
        setPaletteOpen(false);
      }
    };
    window.addEventListener('keydown', keyboard);
    return () => window.removeEventListener('keydown', keyboard);
  }, [setLauncherOpen, setPaletteOpen]);

  return (
    <main className="desktop">
      <TopBar />
      <div className="desktop-canvas" onDoubleClick={() => setPaletteOpen(true)}>
        {windows.filter((item) => !item.minimized).map((windowState) => {
          const Content = APP_CONTENT[windowState.appId];
          return <WindowFrame windowState={windowState} key={windowState.appId}><Content /></WindowFrame>;
        })}
        {launcherOpen ? <AppLauncher /> : null}
        {paletteOpen ? <CommandPalette /> : null}
      </div>
      <Dock />
      <button className="palette-hint" onClick={() => setPaletteOpen(true)}>Command Palette <kbd>Ctrl K</kbd></button>
    </main>
  );
}
