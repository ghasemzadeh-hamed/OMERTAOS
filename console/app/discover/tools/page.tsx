"use client";

import { useEffect, useMemo, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:3000";
const TENANT = process.env.NEXT_PUBLIC_TENANT_ID;

interface ToolResource {
  id: string;
  name: string;
  category: string;
  url: string;
  description?: string;
  tags?: string[];
  source: string;
}

interface RecommendationResponse {
  tools: ToolResource[];
}

export default function DiscoverLatentboxPage() {
  const [scenario, setScenario] = useState<string>("content_marketing");
  const [capabilityFilter, setCapabilityFilter] = useState<string>("all");
  const [tools, setTools] = useState<ToolResource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("scenario", scenario);
    if (capabilityFilter !== "all") {
      params.append("capabilities", capabilityFilter);
    }
    const headers: Record<string, string> = { accept: "application/json", "x-aion-roles": "ROLE_ADMIN" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    setLoading(true);
    fetch(`${CONTROL_BASE}/api/v1/recommendations/tools?${params.toString()}`, {
      credentials: "include",
      headers,
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || "Failed to load latentbox recommendations");
        }
        return res.json();
      })
      .then((data: RecommendationResponse) => {
        setTools(data.tools || []);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [scenario, capabilityFilter]);

  const categories = useMemo(() => {
    const set = new Set(tools.map((tool) => tool.category));
    return Array.from(set);
  }, [tools]);

  const filtered = capabilityFilter === "all" ? tools : tools.filter((tool) => (tool.tags || []).includes(capabilityFilter));

  return (
    <div className="space-y-6 text-right">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold text-white/90">\u06a9\u0634\u0641 \u0627\u0628\u0632\u0627\u0631\u0647\u0627 (Latent Box)</h1>
        <p className="text-sm text-white/70">
          \u0644\u06cc\u0633\u062a \u0627\u0628\u0632\u0627\u0631\u0647\u0627 \u0648 \u0633\u0631\u0648\u06cc\u0633\u200c\u0647\u0627\u06cc \u067e\u06cc\u0634\u0646\u0647\u0627\u062f \u0634\u062f\u0647 \u0627\u0632 latentbox.com \u0628\u0631\u0627\u06cc \u0633\u0646\u0627\u0631\u06cc\u0648\u0647\u0627\u06cc \u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0645\u062d\u062a\u0648\u0627\u060c \u062a\u0648\u0644\u06cc\u062f \u0647\u0646\u0631\u060c \u062a\u062d\u0642\u06cc\u0642 \u0648 \u062a\u0648\u0633\u0639\u0647 \u0627\u06cc\u062c\u0646\u062a.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-white/70">\u0633\u0646\u0627\u0631\u06cc\u0648:</label>
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={scenario}
          onChange={(event) => setScenario(event.target.value)}
        >
          <option value="content_marketing">\u0628\u0627\u0632\u0627\u0631\u06cc\u0627\u0628\u06cc \u0645\u062d\u062a\u0648\u0627</option>
          <option value="gen_art">\u062a\u0648\u0644\u06cc\u062f \u0647\u0646\u0631/\u062a\u0635\u0648\u06cc\u0631</option>
          <option value="research">\u062a\u062d\u0642\u06cc\u0642</option>
          <option value="analysis">\u062a\u062d\u0644\u06cc\u0644 \u062f\u0627\u062f\u0647</option>
          <option value="agent_builder">Agent Builder</option>
        </select>

        <label className="text-sm text-white/70">\u0642\u0627\u0628\u0644\u06cc\u062a:</label>
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={capabilityFilter}
          onChange={(event) => setCapabilityFilter(event.target.value)}
        >
          <option value="all">\u0647\u0645\u0647</option>
          <option value="llm">LLM</option>
          <option value="search">Search</option>
          <option value="image">Image</option>
          <option value="video">Video</option>
          <option value="voice">Voice</option>
        </select>
      </div>

      {loading && <p className="text-sm text-white/60">\u062f\u0631 \u062d\u0627\u0644 \u0628\u0627\u0631\u06af\u0630\u0627\u0631\u06cc \u067e\u06cc\u0634\u0646\u0647\u0627\u062f\u0647\u0627...</p>}
      {error && <p className="text-sm text-red-300">\u062e\u0637\u0627: {error}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        {filtered.map((tool) => (
          <div key={tool.id} className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-white/60">{tool.category}</p>
                <h3 className="text-lg font-semibold text-white/90">{tool.name}</h3>
                <p className="text-xs text-white/50">source: {tool.source}</p>
              </div>
              <a
                href={tool.url}
                className="rounded-xl border border-white/15 bg-white/10 px-3 py-1 text-xs text-white/80 hover:bg-white/20"
                target="_blank"
                rel="noreferrer"
              >
                \u0645\u0634\u0627\u0647\u062f\u0647
              </a>
            </div>
            {tool.description && <p className="mt-3 text-sm text-white/70">{tool.description}</p>}
            <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-white/60">
              {(tool.tags || []).map((tag) => (
                <span key={tag} className="rounded-md bg-white/10 px-2 py-1">#{tag}</span>
              ))}
            </div>
          </div>
        ))}
        {!loading && !filtered.length && (
          <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-white/60">
            \u067e\u06cc\u0634\u0646\u0647\u0627\u062f\u06cc \u06cc\u0627\u0641\u062a \u0646\u0634\u062f\u061b \u0641\u06cc\u0644\u062a\u0631\u0647\u0627 \u0631\u0627 \u062a\u063a\u06cc\u06cc\u0631 \u062f\u0647\u06cc\u062f.
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
        <p>\u0628\u0631\u0627\u06cc \u0647\u0645\u200c\u06af\u0627\u0645\u200c\u0633\u0627\u0632\u06cc \u0644\u06cc\u0633\u062a\u060c \u0627\u0632 \u062f\u0627\u062e\u0644 Control API \u0641\u0631\u0645\u0627\u0646 \u0632\u06cc\u0631 \u0631\u0627 \u0627\u062c\u0631\u0627 \u06a9\u0646\u06cc\u062f:</p>
        <pre className="mt-2 rounded-xl bg-black/30 p-3 text-xs text-white/70">aionctl sync latentbox</pre>
        {categories.length > 0 && (
          <p className="mt-2 text-xs text-white/50">\u062f\u0633\u062a\u0647\u200c\u0647\u0627: {categories.join(", ")}</p>
        )}
      </div>
    </div>
  );
}
