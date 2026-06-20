import type { DesktopSettings } from '../types/shell';

export const OMERTA_CONFIG = {
  consoleUrl: import.meta.env.VITE_OMERTA_CONSOLE_URL ?? 'http://localhost:3000',
  gatewayUrl: import.meta.env.VITE_OMERTA_GATEWAY_URL ?? 'http://localhost:8080',
  controlUrl: import.meta.env.VITE_OMERTA_CONTROL_URL ?? 'http://localhost:8000',
};

export const DEFAULT_SETTINGS: DesktopSettings = {
  ...OMERTA_CONFIG,
  runtimeMode: 'Local',
  compactMode: false,
};

export const SETTINGS_STORAGE_KEY = 'omertaos.desktop.settings.v1';

export function readSettings(): DesktopSettings {
  try {
    const stored = localStorage.getItem(SETTINGS_STORAGE_KEY);
    return stored ? { ...DEFAULT_SETTINGS, ...JSON.parse(stored) } : DEFAULT_SETTINGS;
  } catch {
    return DEFAULT_SETTINGS;
  }
}

export function writeSettings(settings: DesktopSettings): void {
  localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(settings));
}
