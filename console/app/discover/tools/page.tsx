"use client";

import { useEffect, useMemo, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || "http://localhost:8000";
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
        <h1 className="text-2xl font-semibold text-white/90">کشف ابزارها (Latent Box)</h1>
        <p className="text-sm text-white/70">
          لیست ابزارها و سرویس‌های پیشنهاد شده از latentbox.com برای سناریوهای بازاریابی محتوا، تولید هنر، تحقیق و توسعه ایجنت.
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-white/70">سناریو:</label>
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={scenario}
          onChange={(event) => setScenario(event.target.value)}
        >
          <option value="content_marketing">بازاریابی محتوا</option>
          <option value="gen_art">تولید هنر/تصویر</option>
          <option value="research">تحقیق</option>
          <option value="analysis">تحلیل داده</option>
          <option value="agent_builder">Agent Builder</option>
        </select>

        <label className="text-sm text-white/70">قابلیت:</label>
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={capabilityFilter}
          onChange={(event) => setCapabilityFilter(event.target.value)}
        >
          <option value="all">همه</option>
          <option value="llm">LLM</option>
          <option value="search">Search</option>
          <option value="image">Image</option>
          <option value="video">Video</option>
          <option value="voice">Voice</option>
        </select>
      </div>

      {loading && <p className="text-sm text-white/60">در حال بارگذاری پیشنهادها…</p>}
      {error && <p className="text-sm text-red-300">خطا: {error}</p>}

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
                مشاهده
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
            پیشنهادی یافت نشد؛ فیلترها را تغییر دهید.
          </div>
        )}
      </div>

      <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/70">
        <p>برای هم‌گام‌سازی لیست، از داخل Control API فرمان زیر را اجرا کنید:</p>
        <pre className="mt-2 rounded-xl bg-black/30 p-3 text-xs text-white/70">aionctl sync latentbox</pre>
        {categories.length > 0 && (
          <p className="mt-2 text-xs text-white/50">دسته‌ها: {categories.join(", ")}</p>
        )}
      </div>
    </div>
  );
}
