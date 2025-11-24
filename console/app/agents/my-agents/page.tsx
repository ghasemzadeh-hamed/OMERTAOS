"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const GATEWAY_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8080";
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
    fetch(`${GATEWAY_BASE}/api/agents`, { credentials: "include", headers })
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
    const res = await fetch(`${GATEWAY_BASE}/api/agents/${agent.id}/${action}`, {
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
          <h1 className="text-2xl font-semibold text-white/90">Agent\u0647\u0627\u06cc \u0645\u0646</h1>
          <p className="text-sm text-white/70">\u0644\u06cc\u0633\u062a Agent\u0647\u0627\u06cc\u06cc \u06a9\u0647 \u0628\u0631 \u0627\u0633\u0627\u0633 \u0642\u0627\u0644\u0628\u200c\u0647\u0627 \u0633\u0627\u062e\u062a\u0647\u200c\u0627\u06cc\u062f.</p>
        </div>
        <Link
          href="/agents/catalog"
          className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
        >
          \u0627\u0641\u0632\u0648\u062f\u0646 Agent \u062c\u062f\u06cc\u062f
        </Link>
      </div>

      {loading && <p className="text-sm text-white/60">\u062f\u0631 \u062d\u0627\u0644 \u062f\u0631\u06cc\u0627\u0641\u062a Agent\u0647\u0627...</p>}
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
              \u0622\u062e\u0631\u06cc\u0646 \u0628\u0631\u0648\u0632\u0631\u0633\u0627\u0646\u06cc: {new Date(agent.updated_at * 1000).toLocaleString()}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => toggle(agent, "deploy")}
                className="rounded-xl border border-emerald-400/40 bg-emerald-500/20 px-3 py-2 text-xs text-emerald-100 transition hover:bg-emerald-500/30"
              >
                \u0641\u0639\u0627\u0644\u200c\u0633\u0627\u0632\u06cc
              </button>
              <button
                onClick={() => toggle(agent, "disable")}
                className="rounded-xl border border-white/15 bg-white/10 px-3 py-2 text-xs text-white/80 transition hover:bg-white/20"
              >
                \u063a\u06cc\u0631 \u0641\u0639\u0627\u0644 \u06a9\u0631\u062f\u0646
              </button>
            </div>
          </div>
        ))}
        {!loading && !agents.length && (
          <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-white/60">
            \u0647\u06cc\u0686 Agent \u0641\u0639\u0627\u0644\u06cc \u0648\u062c\u0648\u062f \u0646\u062f\u0627\u0631\u062f.
          </div>
        )}
      </div>
    </div>
  );
}
