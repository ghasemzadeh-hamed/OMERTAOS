import { ReactNode } from "react";
import Link from "next/link";
import { redirect } from "next/navigation";
import GlassPanel from "@/components/GlassPanel";
import { safeGetServerSession } from "@/lib/session";

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
  status: "available" | "limited" | "unavailable";
};

const tools: ToolLink[] = [
  {
    href: "/tools/file-explorer",
    label: "File Explorer",
    description: "Sandboxed file API is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/data-studio",
    label: "Data Studio",
    description: "Data preview API is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/editor",
    label: "Text Editor",
    description: "Runtime-backed file editing is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/config-center",
    label: "Routing Policy",
    description: "Propose, apply, and revert Control configuration.",
    minRole: "ADMIN",
    status: "available",
  },
  {
    href: "/tools/system-monitor",
    label: "System Monitor",
    description: "Host resource metrics are not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/services",
    label: "Service Manager",
    description: "Service lifecycle API is not exposed.",
    minRole: "ADMIN",
    status: "unavailable",
  },
  {
    href: "/tools/log-center",
    label: "Log Center",
    description: "Log collection API is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/network",
    label: "Network Proxy Manager",
    description: "Manage source-backed outbound proxy profiles.",
    minRole: "ADMIN",
    status: "available",
  },
  {
    href: "/tools/auth",
    label: "Auth & Roles",
    description: "RBAC administration API is not exposed.",
    minRole: "ADMIN",
    status: "unavailable",
  },
  {
    href: "/tools/models",
    label: "Models",
    description: "Read model metadata reported by the Gateway.",
    minRole: "MANAGER",
    status: "limited",
  },
  {
    href: "/tools/datasets",
    label: "Datasets",
    description: "Dataset ingestion API is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/metrics",
    label: "Metrics",
    description: "Metrics API is not exposed.",
    minRole: "MANAGER",
    status: "unavailable",
  },
  {
    href: "/tools/backup",
    label: "Backup & Snapshot",
    description: "Backup execution API is not exposed.",
    minRole: "ADMIN",
    status: "unavailable",
  },
  {
    href: "/tools/update",
    label: "Update Center",
    description: "Signed update API is not exposed.",
    minRole: "ADMIN",
    status: "unavailable",
  },
  {
    href: "/tools/claude",
    label: "Claude Status",
    description: "Inspect local Claude setup and commands.",
    minRole: "MANAGER",
    status: "available",
  },
];

function normalizeRole(role?: string | null): RoleKey {
  if (!role) return "USER";
  const upper = role.toUpperCase();
  if (upper in rolePriority) {
    return upper as RoleKey;
  }
  return "USER";
}

function filterTools(role: RoleKey) {
  return tools.filter(
    (tool) => rolePriority[role] >= rolePriority[tool.minRole],
  );
}

export default async function ToolsLayout({
  children,
}: {
  children: ReactNode;
}) {
  const session = await safeGetServerSession();
  if (!session) {
    redirect("/login");
  }
  const role = normalizeRole((session.user as any)?.role ?? "USER");
  const available = filterTools(role);

  return (
    <section className="min-h-dvh bg-slate-950/70 px-4 py-6 text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <GlassPanel className="flex flex-col gap-2 rounded-3xl border border-white/10 bg-white/5/30 p-6 backdrop-blur">
          <h1 className="text-3xl font-semibold text-white/90">
            AION System Tools
          </h1>
          <p className="text-sm text-white/70">
            Unified access to auxiliary operations &mdash; file management,
            metrics, networking, RBAC, and lifecycle controls.
          </p>
        </GlassPanel>
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <aside>
            <GlassPanel className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/5/40 p-4 text-right">
              <h2 className="text-lg font-semibold text-white/85">
                Auxiliary tools
              </h2>
              <nav className="space-y-2">
                {available.map((tool) => (
                  <Link
                    key={tool.href}
                    href={tool.href}
                    className="block rounded-2xl border border-transparent bg-white/5 p-3 text-sm transition hover:border-white/20 hover:bg-white/10"
                  >
                    <div className="flex items-center justify-between gap-2 font-medium text-white/85">
                      <span>{tool.label}</span>
                      <span className="text-[10px] font-normal text-white/45">
                        {tool.status}
                      </span>
                    </div>
                    <div className="text-xs text-white/60">
                      {tool.description}
                    </div>
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
