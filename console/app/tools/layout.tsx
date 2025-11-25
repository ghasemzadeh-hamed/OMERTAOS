import { ReactNode } from 'react';
import Link from 'next/link';
import { redirect } from 'next/navigation';
import GlassPanel from '@/components/GlassPanel';
import { safeGetServerSession } from '@/lib/session';

const rolePriority = {
  USER: 0,
  MANAGER: 1,
  ADMIN: 2,
  DEVOPS: 2,
} as const;

type RoleKey = keyof typeof rolePriority;

type ToolLink = {
  href: string;
  label: string;
  description: string;
  minRole: RoleKey;
};

const tools: ToolLink[] = [
  { href: '/tools/file-explorer', label: 'File Explorer', description: 'Browse models, configs, and logs within allowed sandboxes.', minRole: 'MANAGER' },
  { href: '/tools/data-studio', label: 'Data Studio', description: 'Preview CSV or JSON data files for agent workflows.', minRole: 'MANAGER' },
  { href: '/tools/editor', label: 'Text Editor', description: 'Edit YAML/JSON policies and configuration files securely.', minRole: 'MANAGER' },
  { href: '/tools/config-center', label: 'Config Center', description: 'Manage core directories, storage endpoints, and profiles.', minRole: 'ADMIN' },
  { href: '/tools/system-monitor', label: 'System Monitor', description: 'Inspect CPU, memory, GPU, service health, and agent activity.', minRole: 'MANAGER' },
  { href: '/tools/services', label: 'Service Manager', description: 'Start, stop, and restart core services via pluggable backends.', minRole: 'ADMIN' },
  { href: '/tools/log-center', label: 'Log Center', description: 'Tail aggregated logs with search and stream filters.', minRole: 'MANAGER' },
  { href: '/tools/network', label: 'Network Configurator', description: 'Manage API endpoints and TLS certificates.', minRole: 'ADMIN' },
  { href: '/tools/auth', label: 'Auth & Roles', description: 'Assign RBAC roles and mint scoped API tokens.', minRole: 'ADMIN' },
  { href: '/tools/models', label: 'Model Installer', description: 'Install or remove models from registries or remote URLs.', minRole: 'MANAGER' },
  { href: '/tools/datasets', label: 'Dataset Loader', description: 'Register RAG datasets and track indexing status.', minRole: 'MANAGER' },
  { href: '/tools/metrics', label: 'Metrics Dashboard', description: 'Bridge Prometheus/Grafana dashboards or view local stats.', minRole: 'MANAGER' },
  { href: '/tools/backup', label: 'Backup & Snapshot', description: 'Trigger configuration backups and review history.', minRole: 'ADMIN' },
  { href: '/tools/update', label: 'Update Center', description: 'Check and apply platform updates safely.', minRole: 'ADMIN' },
];

function normalizeRole(role?: string | null): RoleKey {
  if (!role) return 'USER';
  const upper = role.toUpperCase();
  if (upper in rolePriority) {
    return upper as RoleKey;
  }
  return 'USER';
}

function filterTools(role: RoleKey) {
  return tools.filter((tool) => rolePriority[role] >= rolePriority[tool.minRole]);
}

export default async function ToolsLayout({ children }: { children: ReactNode }) {
  const session = await safeGetServerSession();
  if (!session) {
    redirect('/login');
  }
  const role = normalizeRole((session.user as any)?.role ?? 'USER');
  const available = filterTools(role);

  return (
    <section className="min-h-dvh bg-slate-950/70 px-4 py-6 text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <GlassPanel className="flex flex-col gap-2 rounded-3xl border border-white/10 bg-white/5/30 p-6 backdrop-blur">
          <h1 className="text-3xl font-semibold text-white/90">AION System Tools</h1>
          <p className="text-sm text-white/70">
            Unified access to auxiliary operations &mdash; file management, metrics, networking, RBAC, and lifecycle controls.
          </p>
        </GlassPanel>
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <aside>
            <GlassPanel className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5/40 p-4 text-right">
              <h2 className="text-lg font-semibold text-white/85">Auxiliary tools</h2>
              <nav className="space-y-2">
                {available.map((tool) => (
                  <Link
                    key={tool.href}
                    href={tool.href}
                    className="block rounded-2xl border border-transparent bg-white/5 p-3 text-sm transition hover:border-white/20 hover:bg-white/10"
                  >
                    <div className="font-medium text-white/85">{tool.label}</div>
                    <div className="text-xs text-white/60">{tool.description}</div>
                  </Link>
                ))}
              </nav>
            </GlassPanel>
          </aside>
          <main>
            <GlassPanel className="min-h-[60vh] rounded-3xl border border-white/10 bg-white/5/20 p-6 text-white/90">
              {children}
            </GlassPanel>
          </main>
        </div>
      </div>
    </section>
  );
}
