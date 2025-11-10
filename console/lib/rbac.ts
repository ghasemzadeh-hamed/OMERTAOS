const roleMatrix = {
  admin: ['dashboard', 'projects', 'tasks', 'agents', 'policies', 'telemetry', 'settings'],
  manager: ['dashboard', 'projects', 'tasks', 'agents', 'policies', 'telemetry'],
  user: ['dashboard', 'projects', 'tasks'],
} as const;

type Role = keyof typeof roleMatrix;

type Resource = (typeof roleMatrix)[Role][number];

const allResources = new Set<Resource>(
  Object.values(roleMatrix).flat() as Resource[],
);

function isResource(value: string): value is Resource {
  return allResources.has(value as Resource);
}

export function canAccess(role: string, resource: string): boolean {
  const normalizedRole = (role.toLowerCase() as Role) ?? 'user';
  const allowed = roleMatrix[normalizedRole] ?? roleMatrix.user;
  const normalizedResource = resource.toLowerCase();
  if (!isResource(normalizedResource)) {
    return false;
  }
  const allowedList = allowed as ReadonlyArray<Resource>;
  return allowedList.includes(normalizedResource);
}
