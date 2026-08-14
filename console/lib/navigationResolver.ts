import { loadCapabilities, loadNavigation, Capability, NavigationModel, NavigationItem } from './schemaLoader';

export type NavigationContext = {
  role: string;
  featureFlags: string[];
};

const criticalRoutes = ['/setup', '/onboarding', '/agents/catalog', '/agents/my-agents'];

function capabilityAllows(capability: Capability, context: NavigationContext): boolean {
  const roleAllowed = capability.rbac.rolesAllowed.includes(context.role);
  const flagsOk = capability.featureFlags.every((flag) => context.featureFlags.includes(flag));
  return roleAllowed && flagsOk;
}

export async function resolveNavigation(context: NavigationContext): Promise<NavigationModel> {
  const [navigation, capabilities] = await Promise.all([loadNavigation(), loadCapabilities()]);
  const filteredItems: NavigationItem[] = navigation.items.filter((item) => {
    const capability = capabilities.find((c) => c.id === item.capabilityId);
    if (!capability) return false;
    return capabilityAllows(capability, context);
  });

  for (const route of criticalRoutes) {
    if (!filteredItems.some((i) => i.route === route)) {
      const fallback = navigation.items.find((i) => i.route === route);
      if (fallback) {
        filteredItems.push(fallback);
      }
    }
  }

  filteredItems.sort((a, b) => a.order - b.order);
  const groups = navigation.groups.slice().sort((a, b) => a.order - b.order);
  return { groups, items: filteredItems };
}

export function getCapabilityForRoute(capabilities: Capability[], route: string): Capability | undefined {
  return capabilities.find((cap) => cap.ui.route === route || cap.ui.pageSchemaRef === route);
}
