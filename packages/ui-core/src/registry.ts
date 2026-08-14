export interface NavigationEntry {
  id: string;
  label: string;
  path: string;
}

export interface DashboardWidget {
  id: string;
  title: string;
  description: string;
  field: string;
}

export interface QuickLink {
  id: string;
  navigationRef: string;
}

export interface PageDefinition {
  id: string;
  title: string;
  widgets: DashboardWidget[];
  quickLinks: QuickLink[];
}

export const registry: {
  navigation: NavigationEntry[];
  pages: Record<string, PageDefinition>;
} = {
  navigation: [
    { id: 'dashboard', label: 'Dashboard', path: '/' },
    { id: 'agents', label: 'Agents', path: '/agents/catalog' },
    { id: 'models', label: 'Models', path: '/tools/models' },
    { id: 'health', label: 'Health', path: '/status' },
  ],
  pages: {
    dashboard: {
      id: 'dashboard',
      title: 'Dashboard',
      widgets: [
        {
          id: 'gateway',
          title: 'Gateway',
          description: 'HTTP API status',
          field: 'services.gateway.status',
        },
        {
          id: 'control',
          title: 'Control',
          description: 'Control-plane status',
          field: 'services.control.status',
        },
        {
          id: 'console',
          title: 'Console',
          description: 'Console service status',
          field: 'services.console.status',
        },
      ],
      quickLinks: [
        { id: 'agents', navigationRef: 'agents' },
        { id: 'models', navigationRef: 'models' },
        { id: 'health', navigationRef: 'health' },
      ],
    },
  },
};

export function findNavById(id: string): NavigationEntry | undefined {
  return registry.navigation.find((entry) => entry.id === id);
}
