const roleMatrix = {
  admin: ['dashboard', 'projects', 'tasks', 'agents', 'policies', 'telemetry', 'settings'],
  manager: ['dashboard', 'projects', 'tasks', 'agents', 'policies', 'telemetry'],
  user: ['dashboard', 'projects', 'tasks'],
} as const;

type Role = keyof typeof roleMatrix;

type Resource = (typeof roleMatrix)[Role][number];

export function canAccess(role: string, resource: string): boolean {
  const normalizedRole = (role.toLowerCase() as Role) ?? 'user';
  const allowed = roleMatrix[normalizedRole] ?? roleMatrix.user;
  return allowed.includes(resource as Resource);
}
