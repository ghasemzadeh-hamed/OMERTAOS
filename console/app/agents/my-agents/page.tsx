"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || "http://localhost:8000";
const TENANT = process.env.NEXT_PUBLIC_TENANT_ID;

type AgentInstance = {
  id: string;
  template_id: string;
  name: string;
  status: string;
  scope: string;
  enabled: boolean;
  updated_at: number;
};

export default function MyAgentsPage() {
  const [agents, setAgents] = useState<AgentInstance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const headers: Record<string, string> = { accept: "application/json", "content-type": "application/json" };
  if (TENANT) {
    headers["tenant-id"] = TENANT;
  }

  const load = () => {
    setLoading(true);
    fetch(`${CONTROL_BASE}/api/agents`, { credentials: "include", headers })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || "Failed to load agents");
        }
        return res.json();
      })
      .then((data: AgentInstance[]) => setAgents(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const toggle = async (agent: AgentInstance, action: "deploy" | "disable") => {
    const res = await fetch(`${CONTROL_BASE}/api/agents/${agent.id}/${action}`, {
      method: "POST",
      credentials: "include",
      headers,
    });
    if (!res.ok) {
      const detail = await res.text();
      setError(detail || `Failed to ${action}`);
      return;
    }
    const updated = (await res.json()) as AgentInstance;
    setAgents((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
  };

  return (
    <div className="space-y-6 text-right">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold text-white/90">Agentهای من</h1>
          <p className="text-sm text-white/70">لیست Agentهایی که بر اساس قالب‌ها ساخته‌اید.</p>
        </div>
        <Link
          href="/agents/catalog"
          className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
        >
          افزودن Agent جدید
        </Link>
      </div>

      {loading && <p className="text-sm text-white/60">در حال دریافت Agentها…</p>}
      {error && <p className="text-sm text-red-300">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        {agents.map((agent) => (
          <div key={agent.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-white/60">{agent.scope}</p>
                <h3 className="text-lg font-semibold text-white/90">{agent.name}</h3>
                <p className="text-xs text-white/50">Template: {agent.template_id}</p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs ${
                  agent.enabled ? "bg-emerald-500/20 text-emerald-100" : "bg-white/10 text-white/70"
                }`}
              >
                {agent.status}
              </span>
            </div>
            <p className="mt-2 text-xs text-white/60">
              آخرین بروزرسانی: {new Date(agent.updated_at * 1000).toLocaleString()}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => toggle(agent, "deploy")}
                className="rounded-xl border border-emerald-400/40 bg-emerald-500/20 px-3 py-2 text-xs text-emerald-100 transition hover:bg-emerald-500/30"
              >
                فعال‌سازی
              </button>
              <button
                onClick={() => toggle(agent, "disable")}
                className="rounded-xl border border-white/15 bg-white/10 px-3 py-2 text-xs text-white/80 transition hover:bg-white/20"
              >
                غیر فعال کردن
              </button>
            </div>
          </div>
        ))}
        {!loading && !agents.length && (
          <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-white/60">
            هیچ Agent فعالی وجود ندارد.
          </div>
        )}
      </div>
    </div>
  );
}
