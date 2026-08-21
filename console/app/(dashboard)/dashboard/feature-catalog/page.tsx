import Link from "next/link";

type CapabilityStatus = "available" | "limited" | "unavailable";
type CapabilityItem = readonly [
  href: string,
  label: string,
  status: CapabilityStatus,
];
type CapabilityGroup = { name: string; items: CapabilityItem[] };

const groups: CapabilityGroup[] = [
  {
    name: "AI and workflows",
    items: [
      ["/chat", "Chat", "available"],
      ["/agent-chat", "Agent chat", "limited"],
      ["/agent", "Agent mode", "limited"],
      ["/tasks", "Tasks", "unavailable"],
      ["/agents/my-agents", "My agents", "unavailable"],
      ["/agents/catalog", "Agent catalog", "unavailable"],
    ],
  },
  {
    name: "Operations",
    items: [
      ["/dashboard/health", "System health", "available"],
      ["/tools/system-monitor", "System monitor", "unavailable"],
      ["/tools/services", "Service manager", "unavailable"],
      ["/tools/log-center", "Log center", "unavailable"],
      ["/tools/update", "Update center", "unavailable"],
      ["/tools/backup", "Backup and snapshot", "unavailable"],
      ["/tools/metrics", "Metrics", "unavailable"],
    ],
  },
  {
    name: "Configuration and data",
    items: [
      ["/tools/config-center", "Routing policy", "available"],
      ["/tools/models", "Models", "limited"],
      ["/tools/datasets", "Datasets", "unavailable"],
      ["/tools/data-studio", "Data studio", "unavailable"],
      ["/tools/network", "Network proxy manager", "available"],
      ["/tools/file-explorer", "File explorer", "unavailable"],
      ["/tools/editor", "Policy editor", "unavailable"],
      ["/tools/auth", "Auth and roles", "unavailable"],
    ],
  },
  {
    name: "Extensions and administration",
    items: [
      ["/tools/discovery", "Tool discovery", "unavailable"],
      ["/tools/claude", "Claude status", "available"],
      ["/dashboard/feature-catalog", "Capability catalog", "available"],
      ["/admin/config", "Admin configuration", "available"],
      ["/admin/tenancy", "Tenancy", "unavailable"],
      ["/integrations/windows-bridge", "Windows bridge", "limited"],
    ],
  },
];

const statusTone = {
  available: "bg-emerald-400/15 text-emerald-100",
  limited: "bg-amber-400/15 text-amber-100",
  unavailable: "bg-white/10 text-white/55",
} as const;

export default function FeatureCatalogPage() {
  const routes = groups.flatMap((group) => group.items);
  const available = routes.filter(
    ([, , status]) => status === "available",
  ).length;
  const limited = routes.filter(([, , status]) => status === "limited").length;

  return (
    <main className="min-h-dvh bg-slate-950 px-4 py-8 text-white">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-wrap items-end justify-between gap-4 border-b border-white/10 pb-5">
          <div>
            <h1 className="text-2xl font-semibold">
              Console capability catalog
            </h1>
            <p className="mt-1 text-sm text-white/60">
              Current routes and backend availability. Unavailable pages do not
              expose fake controls.
            </p>
          </div>
          <p className="text-xs text-white/50">
            {available} available / {limited} limited / {routes.length} total
          </p>
        </header>

        {groups.map((group) => (
          <section key={group.name} className="space-y-3">
            <h2 className="text-sm font-semibold uppercase text-white/55">
              {group.name}
            </h2>
            <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
              {group.items.map(([href, label, status]) => (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center justify-between gap-3 border border-white/10 bg-white/5 px-4 py-3 hover:bg-white/10"
                >
                  <span className="font-medium text-white/85">{label}</span>
                  <span
                    className={`px-2 py-1 text-[11px] ${statusTone[status]}`}
                  >
                    {status}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </main>
  );
}
