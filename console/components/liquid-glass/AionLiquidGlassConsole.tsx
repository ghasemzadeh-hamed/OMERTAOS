'use client';

import Link from 'next/link';
import { signOut, useSession } from 'next-auth/react';
import React, { useEffect, useMemo, useState, type JSX } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Archive,
  Bot,
  Boxes,
  Cable,
  ChevronLeft,
  ChevronRight,
  Database,
  DownloadCloud,
  FileText,
  Gauge,
  HardDrive,
  KeyRound,
  LayoutDashboard,
  ListTodo,
  MessageSquare,
  Moon,
  PackageSearch,
  Plug,
  RefreshCcw,
  Search,
  Server,
  Settings,
  ShieldCheck,
  Sun,
  TerminalSquare,
  Users,
  Workflow,
  Wrench,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const glass =
  'backdrop-blur-xl bg-white/10 dark:bg-white/5 border border-white/20 dark:border-white/10 shadow-[0_8px_30px_rgb(0,0,0,0.12)]';

const primaryNav = [
  { href: '/console', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/chat', label: 'Chat', icon: MessageSquare },
  { href: '/agents/catalog', label: 'Agents', icon: Bot },
  { href: '/tasks', label: 'Tasks', icon: ListTodo },
  { href: '/tools/update', label: 'Updates', icon: RefreshCcw },
  { href: '/tools/config-center', label: 'Configuration', icon: Settings },
  { href: '/tools/models', label: 'Installers', icon: DownloadCloud },
  { href: '/dashboard/health', label: 'Health', icon: ShieldCheck },
  { href: '/tools', label: 'Tools', icon: Wrench },
] as const;

type ConsoleRole = 'USER' | 'MANAGER' | 'ADMIN' | 'DEVOPS';

type Surface = {
  href: string;
  label: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  minRole: ConsoleRole;
};

const surfaceGroups: ReadonlyArray<{ label: string; items: ReadonlyArray<Surface> }> = [
  {
    label: 'AI & workflows',
    items: [
      { href: '/chat', label: 'Chat', description: 'Create and continue assistant threads.', icon: MessageSquare, minRole: 'USER' },
      { href: '/agent-chat', label: 'Agent chat', description: 'Run focused conversations with agents.', icon: Workflow, minRole: 'USER' },
      { href: '/agent', label: 'Agent mode', description: 'Operate an agent with tool execution.', icon: Bot, minRole: 'USER' },
      { href: '/tasks', label: 'Tasks', description: 'Track queued and completed work.', icon: ListTodo, minRole: 'USER' },
      { href: '/agents/my-agents', label: 'My agents', description: 'Manage deployed agent instances.', icon: Users, minRole: 'USER' },
      { href: '/agents/catalog', label: 'Agent catalog', description: 'Browse and deploy agent templates.', icon: PackageSearch, minRole: 'USER' },
    ],
  },
  {
    label: 'Operations',
    items: [
      { href: '/dashboard/health', label: 'System health', description: 'Inspect live dependency and service health.', icon: ShieldCheck, minRole: 'USER' },
      { href: '/tools/system-monitor', label: 'System monitor', description: 'Inspect CPU, memory, GPU, and activity.', icon: Activity, minRole: 'MANAGER' },
      { href: '/tools/services', label: 'Service manager', description: 'Control supported platform services.', icon: Server, minRole: 'ADMIN' },
      { href: '/tools/log-center', label: 'Log center', description: 'Search and stream aggregated logs.', icon: FileText, minRole: 'MANAGER' },
      { href: '/tools/update', label: 'Update center', description: 'Check and apply platform updates.', icon: RefreshCcw, minRole: 'ADMIN' },
      { href: '/tools/backup', label: 'Backup & snapshot', description: 'Create backups and inspect history.', icon: Archive, minRole: 'ADMIN' },
      { href: '/tools/metrics', label: 'Metrics', description: 'Inspect metrics and monitoring integrations.', icon: Gauge, minRole: 'MANAGER' },
    ],
  },
  {
    label: 'Configuration & data',
    items: [
      { href: '/tools/config-center', label: 'Config center', description: 'Manage runtime paths, profiles, and policy.', icon: Settings, minRole: 'ADMIN' },
      { href: '/tools/models', label: 'Model installer', description: 'Install and remove model packages.', icon: DownloadCloud, minRole: 'MANAGER' },
      { href: '/tools/datasets', label: 'Datasets', description: 'Register and index RAG datasets.', icon: Database, minRole: 'MANAGER' },
      { href: '/tools/data-studio', label: 'Data studio', description: 'Preview structured workflow data.', icon: Boxes, minRole: 'MANAGER' },
      { href: '/tools/network', label: 'Network', description: 'Manage endpoints and TLS configuration.', icon: Plug, minRole: 'ADMIN' },
      { href: '/tools/file-explorer', label: 'File explorer', description: 'Browse allowed workspace paths.', icon: HardDrive, minRole: 'MANAGER' },
      { href: '/tools/editor', label: 'Policy editor', description: 'Edit supported YAML and JSON files.', icon: TerminalSquare, minRole: 'MANAGER' },
      { href: '/tools/auth', label: 'Auth & roles', description: 'Manage RBAC roles and scoped tokens.', icon: KeyRound, minRole: 'ADMIN' },
    ],
  },
  {
    label: 'Extensions & administration',
    items: [
      { href: '/tools/discovery', label: 'Tool discovery', description: 'Discover registered platform tools.', icon: Search, minRole: 'USER' },
      { href: '/tools/claude', label: 'Claude marketplace', description: 'Inspect Claude Code and plugin setup.', icon: Cable, minRole: 'MANAGER' },
      { href: '/dashboard/feature-catalog', label: 'Feature catalog', description: 'Review available product capabilities.', icon: LayoutDashboard, minRole: 'USER' },
      { href: '/admin/config', label: 'Admin configuration', description: 'Manage administrative configuration.', icon: Settings, minRole: 'ADMIN' },
      { href: '/admin/tenancy', label: 'Tenancy', description: 'Manage tenant-level settings.', icon: Users, minRole: 'ADMIN' },
      { href: '/integrations/windows-bridge', label: 'Windows bridge', description: 'Configure Windows and WSL integration.', icon: Cable, minRole: 'ADMIN' },
    ],
  },
];

const rolePriority: Record<ConsoleRole, number> = {
  USER: 0,
  MANAGER: 1,
  ADMIN: 2,
  DEVOPS: 2,
};

const THEME_STORAGE_KEY = 'aion-liquid-theme';

type ServiceState = 'ok' | 'healthy' | 'degraded' | 'down' | 'error' | 'unknown';

type HealthResponse = {
  status?: ServiceState;
  services?: Record<string, { status?: ServiceState; details?: string }>;
  updatedAt?: string;
};

type ConfigStatusResponse = {
  effective?: Record<string, unknown>;
  router?: Record<string, unknown>;
  policy?: Record<string, unknown>;
  [key: string]: unknown;
};

function statusTone(status?: ServiceState) {
  if (status === 'ok' || status === 'healthy') return 'bg-emerald-500/80';
  if (status === 'degraded') return 'bg-amber-500/80';
  if (status === 'down' || status === 'error') return 'bg-rose-500/80';
  return 'bg-slate-500/80';
}

function readString(source: unknown, keys: string[], fallback = 'Unknown') {
  if (!source || typeof source !== 'object') return fallback;
  for (const key of keys) {
    const value = (source as Record<string, unknown>)[key];
    if (typeof value === 'string' && value.trim()) return value;
    if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  }
  return fallback;
}

function normalizeRole(role?: string | null): ConsoleRole {
  const normalized = role?.toUpperCase();
  return normalized && normalized in rolePriority ? (normalized as ConsoleRole) : 'USER';
}

export default function AionLiquidGlassConsole(): JSX.Element {
  const { data: session } = useSession();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [dark, setDark] = useState(true);
  const [project, setProject] = useState('local');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [configStatus, setConfigStatus] = useState<ConfigStatusResponse | null>(null);
  const [healthError, setHealthError] = useState<string | null>(null);
  const [configError, setConfigError] = useState<string | null>(null);

  useEffect(() => {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (storedTheme === 'light') {
      setDark(false);
    } else if (storedTheme === 'dark') {
      setDark(true);
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(THEME_STORAGE_KEY, dark ? 'dark' : 'light');
  }, [dark]);

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      try {
        const res = await fetch('/api/system/health', { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setHealth(data);
          setHealthError(null);
        }
      } catch (error) {
        if (!cancelled) setHealthError(error instanceof Error ? error.message : 'Unable to load health');
      }

      try {
        const res = await fetch('/api/system/admin/config/status', { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        if (!cancelled) {
          setConfigStatus(data);
          setConfigError(null);
        }
      } catch (error) {
        if (!cancelled) setConfigError(error instanceof Error ? error.message : 'Unable to load config');
      }
    }

    void loadStatus();
    const id = window.setInterval(loadStatus, 30_000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const themeClasses = useMemo(
    () => `${dark ? 'dark' : ''} bg-gradient-to-br from-[#0f172a] via-[#111827] to-[#030712]`,
    [dark],
  );

  const services = health?.services ?? {};
  const overallStatus = health?.status ?? (healthError ? 'error' : 'unknown');
  const effectiveConfig = configStatus?.effective ?? configStatus?.router ?? configStatus?.policy ?? configStatus;
  const currentRole = normalizeRole((session?.user as { role?: string } | undefined)?.role);

  return (
    <div dir="ltr" className={`min-h-screen ${themeClasses} text-white`}>
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-24 -left-24 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute -bottom-24 -right-24 h-[32rem] w-[32rem] rounded-full bg-fuchsia-500/10 blur-3xl" />
      </div>

      <div className="relative z-10 flex min-h-screen">
        <motion.aside
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: 'spring', stiffness: 60, damping: 12 }}
          className={`${glass} ${sidebarOpen ? 'w-80' : 'w-20'} sticky top-4 m-4 flex h-[calc(100vh-2rem)] min-h-0 flex-col gap-3 rounded-2xl p-3`}
        >
          <div className="flex items-center justify-between px-2 py-1">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6" />
              {sidebarOpen && <span className="font-bold">AION-OS</span>}
            </div>
            <Button size="icon" variant="ghost" onClick={() => setSidebarOpen((prev) => !prev)} aria-label="Toggle navigation">
              {sidebarOpen ? <ChevronRight /> : <ChevronLeft />}
            </Button>
          </div>

          <div className="px-2">
            <Select value={project} onValueChange={setProject}>
              <SelectTrigger className={`${glass} h-10`} aria-label="Choose project">
                <SelectValue placeholder="Choose project" />
              </SelectTrigger>
              <SelectContent align="end">
                <SelectItem value="local">Local workspace</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <nav className="mt-2 flex flex-col gap-1" aria-label="Primary console navigation">
            {primaryNav.map((item) => {
              const Icon = item.icon;
              return (
                <Button key={item.href} asChild variant={item.href === '/console' ? 'default' : 'ghost'} className="justify-start hover:bg-white/10">
                  <Link href={item.href}>
                    <Icon className="ml-3 h-5 w-5" />
                    {sidebarOpen && <span>{item.label}</span>}
                  </Link>
                </Button>
              );
            })}
          </nav>

          {sidebarOpen && (
            <div className="mt-2 min-h-0 flex-1 overflow-y-auto border-t border-white/10 pt-3 pr-1">
              {surfaceGroups.map((group) => (
                <section key={group.label} className="mb-4">
                  <h2 className="px-2 pb-1 text-xs font-semibold uppercase text-white/50">{group.label}</h2>
                  <nav className="space-y-0.5" aria-label={group.label}>
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const permitted = rolePriority[currentRole] >= rolePriority[item.minRole];
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className="flex min-h-9 items-center gap-2 rounded-md px-2 py-1.5 text-sm text-white/80 hover:bg-white/10"
                          title={item.description}
                        >
                          <Icon className="h-4 w-4 shrink-0" />
                          <span className="min-w-0 flex-1 truncate">{item.label}</span>
                          {!permitted && <span className="text-[10px] text-amber-200">{item.minRole}</span>}
                        </Link>
                      );
                    })}
                  </nav>
                </section>
              ))}
            </div>
          )}

          <div className="px-2">
            <Card className={`${glass} rounded-xl`}>
              <CardContent className="space-y-3 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    <span className="text-sm">Service status</span>
                  </div>
                  <Badge className={statusTone(overallStatus)}>{overallStatus}</Badge>
                </div>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(services).length ? (
                    Object.entries(services).map(([name, service]) => (
                      <Badge key={name} className={statusTone(service.status)}>
                        {name}
                      </Badge>
                    ))
                  ) : (
                    <span className="text-xs text-white/55">{healthError ?? 'Loading service health...'}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.aside>

        <main className="m-4 mr-0 flex-1 space-y-4 pr-4">
          <div className={`${glass} flex items-center justify-between rounded-2xl px-4 py-3`}>
            <div className="flex items-center gap-3">
              <span className="font-semibold">Operations overview</span>
              <Badge className={statusTone(overallStatus)}>{overallStatus}</Badge>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" onClick={() => setDark((prev) => !prev)} className="gap-2">
                {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                <span>Theme</span>
              </Button>
              <Button variant="secondary" className="bg-white/20 hover:bg-white/30" onClick={() => void signOut({ callbackUrl: '/login' })}>
                Sign out
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
            <Card className={`${glass} rounded-2xl xl:col-span-2`}>
              <CardHeader>
                <CardTitle>System summary</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 gap-3 md:grid-cols-3">
                <Stat title="Gateway" value={services.gateway?.status ?? 'unknown'} sub={services.gateway?.details ?? healthError ?? 'Waiting for health API'} />
                <Stat title="Control" value={services.control?.status ?? 'unknown'} sub={services.control?.details ?? 'Reported by Gateway health'} />
                <Stat title="Console" value={services.console?.status ?? 'unknown'} sub={services.console?.details ?? 'Local health endpoint'} />
              </CardContent>
            </Card>

            <Card className={`${glass} rounded-2xl`}>
              <CardHeader>
                <CardTitle>Current router</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <KeyValue k="Policy" v={readString(effectiveConfig, ['policy', 'routing_policy', 'mode'])} />
                <KeyValue k="Local provider" v={readString(effectiveConfig, ['local_provider', 'localProvider', 'default_model'])} />
                <KeyValue k="API provider" v={readString(effectiveConfig, ['api_provider', 'apiProvider', 'provider'])} />
                {configError && <p className="text-xs text-amber-200">Config status unavailable: {configError}</p>}
                <Button asChild className="w-full bg-white/20 hover:bg-white/30">
                  <Link href="/tools/config-center">Edit policy</Link>
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card className={`${glass} rounded-2xl`}>
            <CardHeader>
              <CardTitle>Quick actions</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <ActionLink href="/chat" icon={MessageSquare} label="Open chat" />
              <ActionLink href="/tools/update" icon={RefreshCcw} label="Check updates" />
              <ActionLink href="/tools/models" icon={DownloadCloud} label="Install models" />
              <ActionLink href="/tools/system-monitor" icon={Activity} label="Inspect services" />
            </CardContent>
          </Card>

          <Card className={`${glass} rounded-2xl`}>
            <CardHeader>
              <CardTitle>All console capabilities</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {surfaceGroups.map((group) => (
                <section key={group.label}>
                  <h2 className="mb-2 text-sm font-semibold uppercase text-white/55">{group.label}</h2>
                  <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
                    {group.items.map((item) => {
                      const Icon = item.icon;
                      const permitted = rolePriority[currentRole] >= rolePriority[item.minRole];
                      return (
                        <Link key={item.href} href={item.href} className="flex min-h-20 items-start gap-3 rounded-md border border-white/10 bg-white/5 px-3 py-3 hover:bg-white/10">
                          <Icon className="mt-0.5 h-5 w-5 shrink-0 text-cyan-200" />
                          <span className="min-w-0 flex-1">
                            <span className="flex items-center justify-between gap-2 font-medium">
                              {item.label}
                              {!permitted && <span className="text-[10px] text-amber-200">{item.minRole}</span>}
                            </span>
                            <span className="mt-1 block text-xs leading-5 text-white/55">{item.description}</span>
                          </span>
                        </Link>
                      );
                    })}
                  </div>
                </section>
              ))}
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}

type StatProps = {
  title: string;
  value: string;
  sub?: string;
};

function Stat({ title, value, sub }: StatProps) {
  return (
    <div className={`${glass} rounded-xl p-4`}>
      <div className="text-sm opacity-80">{title}</div>
      <div className="mt-1 text-2xl font-extrabold capitalize">{value}</div>
      {sub && <div className="mt-1 line-clamp-2 text-xs opacity-70">{sub}</div>}
    </div>
  );
}

type KeyValueProps = {
  k: string;
  v: string;
};

function KeyValue({ k, v }: KeyValueProps) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5">
      <span className="text-sm opacity-90">{k}</span>
      <span className="truncate text-right text-sm opacity-80">{v}</span>
    </div>
  );
}

type ActionLinkProps = {
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
};

function ActionLink({ href, icon: Icon, label }: ActionLinkProps) {
  return (
    <Button asChild variant="secondary" className="h-12 justify-start bg-white/15 hover:bg-white/25">
      <Link href={href}>
        <Icon className="mr-2 h-4 w-4" />
        {label}
      </Link>
    </Button>
  );
}
