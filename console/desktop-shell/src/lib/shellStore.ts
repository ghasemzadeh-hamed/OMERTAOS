import { create } from 'zustand';
import type { AppId, ShellWindow } from '../types/shell';

interface ShellState {
  windows: ShellWindow[];
  launcherOpen: boolean;
  paletteOpen: boolean;
  openApp: (appId: AppId) => void;
  closeApp: (appId: AppId) => void;
  focusApp: (appId: AppId) => void;
  toggleMinimize: (appId: AppId) => void;
  toggleMaximize: (appId: AppId) => void;
  setLauncherOpen: (open: boolean) => void;
  setPaletteOpen: (open: boolean) => void;
}

const nextZIndex = (windows: ShellWindow[]) =>
  windows.reduce((highest, item) => Math.max(highest, item.zIndex), 0) + 1;

export const useShellStore = create<ShellState>((set) => ({
  windows: [{ appId: 'console', minimized: false, maximized: false, zIndex: 1 }],
  launcherOpen: false,
  paletteOpen: false,
  openApp: (appId) =>
    set((state) => {
      const existing = state.windows.find((item) => item.appId === appId);
      const zIndex = nextZIndex(state.windows);
      return {
        launcherOpen: false,
        paletteOpen: false,
        windows: existing
          ? state.windows.map((item) =>
              item.appId === appId ? { ...item, minimized: false, zIndex } : item,
            )
          : [...state.windows, { appId, minimized: false, maximized: false, zIndex }],
      };
    }),
  closeApp: (appId) =>
    set((state) => ({ windows: state.windows.filter((item) => item.appId !== appId) })),
  focusApp: (appId) =>
    set((state) => ({
      windows: state.windows.map((item) =>
        item.appId === appId ? { ...item, zIndex: nextZIndex(state.windows) } : item,
      ),
    })),
  toggleMinimize: (appId) =>
    set((state) => ({
      windows: state.windows.map((item) =>
        item.appId === appId ? { ...item, minimized: !item.minimized } : item,
      ),
    })),
  toggleMaximize: (appId) =>
    set((state) => ({
      windows: state.windows.map((item) =>
        item.appId === appId ? { ...item, maximized: !item.maximized, minimized: false } : item,
      ),
    })),
  setLauncherOpen: (launcherOpen) => set({ launcherOpen, paletteOpen: false }),
  setPaletteOpen: (paletteOpen) => set({ paletteOpen, launcherOpen: false }),
}));
