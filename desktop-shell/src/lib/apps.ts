import { Bot, Box, Files, Gauge, Monitor, ServerCog, Settings, SquareTerminal } from 'lucide-react';
import type { ShellApp } from '../types/shell';

export const SHELL_APPS: ShellApp[] = [
  { id: 'console', label: 'Console', windowTitle: 'Web Console', description: 'Open the Web Console', icon: Monitor },
  { id: 'agents', label: 'Agent Center', description: 'Agents and templates', icon: Bot },
  { id: 'terminal', label: 'Terminal', description: 'Policy-gated terminal', icon: SquareTerminal },
  { id: 'files', label: 'Files', description: 'Capability-gated files', icon: Files },
  { id: 'models', label: 'Models', description: 'Model registry', icon: Box },
  { id: 'services', label: 'Services', description: 'Service inventory', icon: ServerCog },
  { id: 'monitor', label: 'Monitor', description: 'System health', icon: Gauge },
  { id: 'settings', label: 'Settings', description: 'Desktop configuration', icon: Settings },
];

export const APP_BY_ID = new Map(SHELL_APPS.map((app) => [app.id, app]));
