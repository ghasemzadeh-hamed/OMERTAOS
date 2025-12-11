import fs from 'fs/promises';
import path from 'path';

export type CapabilityEndpoint = { service: 'gateway' | 'control'; method: string; path: string };
export type Capability = {
  id: string;
  title: string;
  description: string;
  rbac: { rolesAllowed: string[] };
  featureFlags: string[];
  endpoints: CapabilityEndpoint[];
  ui: { route: string; pageSchemaRef: string; navGroup: string; navIcon?: string };
  tenancy: { needsTenantHeader: boolean };
};

export type NavigationGroup = { id: string; title: string; order: number };
export type NavigationItem = {
  id: string;
  title: string;
  route: string;
  groupId: string;
  capabilityId: string;
  order: number;
  icon?: string;
};

export type NavigationModel = { groups: NavigationGroup[]; items: NavigationItem[] };

export type PageSchema = {
  id: string;
  route: string;
  title: string;
  description: string;
  layout: string;
  sections: any[];
  dataSources?: any[];
};

const rootConfig = path.resolve(process.cwd(), '..', 'config');

export async function loadCapabilities(): Promise<Capability[]> {
  const file = await fs.readFile(path.join(rootConfig, 'capabilities.json'), 'utf-8');
  const parsed = JSON.parse(file);
  return parsed.capabilities as Capability[];
}

export async function loadNavigation(): Promise<NavigationModel> {
  const file = await fs.readFile(path.join(rootConfig, 'navigation.json'), 'utf-8');
  return JSON.parse(file) as NavigationModel;
}

export async function loadPageSchema(route: string): Promise<PageSchema | null> {
  const pagesDir = path.join(rootConfig, 'pages');
  const entries = await fs.readdir(pagesDir);
  for (const entry of entries) {
    if (!entry.endsWith('.json')) continue;
    const contents = await fs.readFile(path.join(pagesDir, entry), 'utf-8');
    const schema = JSON.parse(contents) as PageSchema;
    if (schema.route === route) {
      return schema;
    }
  }
  return null;
}

export async function resolvePageSchemaById(pageSchemaRef: string): Promise<PageSchema | null> {
  const pagesDir = path.join(rootConfig, 'pages');
  const file = path.join(pagesDir, pageSchemaRef);
  try {
    const contents = await fs.readFile(file, 'utf-8');
    return JSON.parse(contents) as PageSchema;
  } catch (err) {
    console.error('Failed to resolve page schema', pageSchemaRef, err);
    return null;
  }
}
