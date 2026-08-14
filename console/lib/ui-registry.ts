import { registry, findNavById, PageDefinition, NavigationEntry } from '../../packages/ui-core/src/registry';

export { registry, findNavById };

export function dashboardPage(): PageDefinition {
  return registry.pages.dashboard;
}

export function navigationEntries(): NavigationEntry[] {
  return registry.navigation;
}
