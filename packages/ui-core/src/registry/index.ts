import navigation from '../../registry/navigation.json';
import capabilities from '../../registry/capabilities.json';
import dashboardPage from '../../registry/pages/dashboard.page.json';

export type NavigationEntry = {
  id: string;
  label: string;
  path: string;
  rolesAllowed: string[];
  featureFlags: string[];
};

export type WidgetDefinition = {
  id: string;
  title: string;
  description: string;
  endpointRef: string;
  field: string;
};

export type QuickLinkDefinition = {
  id: string;
  navigationRef: string;
};

export type PageDefinition = {
  id: string;
  widgets: WidgetDefinition[];
  quickLinks: QuickLinkDefinition[];
};

export type Registry = {
  navigation: NavigationEntry[];
  capabilities: typeof capabilities;
  pages: Record<string, PageDefinition>;
};

export const registry: Registry = {
  navigation,
  capabilities,
  pages: {
    dashboard: dashboardPage,
  },
};

export function findNavById(id: string): NavigationEntry | undefined {
  return registry.navigation.find((item) => item.id === id);
}
