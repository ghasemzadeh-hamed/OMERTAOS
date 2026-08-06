import type { LucideIcon } from 'lucide-react';

export type AppId =
  | 'console'
  | 'agents'
  | 'terminal'
  | 'files'
  | 'models'
  | 'services'
  | 'monitor'
  | 'settings';

export type RuntimeMode = 'Local' | 'WSL' | 'Linux' | 'Bare Metal';
export type ServiceState = 'online' | 'offline' | 'checking';

export interface ShellApp {
  id: AppId;
  label: string;
  windowTitle?: string;
  description: string;
  icon: LucideIcon;
}

export interface ShellWindow {
  appId: AppId;
  minimized: boolean;
  maximized: boolean;
  zIndex: number;
}

export interface DesktopSettings {
  consoleUrl: string;
  gatewayUrl: string;
  runtimeMode: RuntimeMode;
  compactMode: boolean;
}
