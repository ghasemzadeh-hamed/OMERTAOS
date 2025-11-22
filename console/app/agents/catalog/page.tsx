"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || "http://localhost:8000";
const TENANT = process.env.NEXT_PUBLIC_TENANT_ID;

type AgentTemplate = {
  id: string;
  name: string;
  category: string;
  framework: string;
  description?: string;
  capabilities?: string[];
  tags?: string[];
  icon?: string;
};

type CatalogResponse = {
  agents: AgentTemplate[];
};

export default function AgentCatalogPage() {
  const [templates, setTemplates] = useState<AgentTemplate[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const headers: Record<string, string> = { accept: "application/json" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    fetch(`${CONTROL_BASE}/api/agent-catalog`, { credentials: "include", headers })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || "Failed to load agent catalog");
        }
        return res.json();
      })
      .then((data: CatalogResponse) => {
        setTemplates(data.agents || []);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  const categories = useMemo(() => {
    const set = new Set(templates.map((template) => template.category));
    return ["all", ...Array.from(set)];
  }, [templates]);

  const filtered = templates.filter(
    (template) => categoryFilter === "all" || template.category === categoryFilter,
  );

  return (
    <div className="space-y-6 text-right">
      <div className="space-y-2">
        <h1 className="text-2xl font-semibold text-white/90">کاتالوگ عامل‌ها</h1>
        <p className="text-sm text-white/70">
          قالب‌های آماده برای CrewAI، AutoGPT، SuperAGI و سایر فریم‌ورک‌ها. یک قالب را انتخاب کنید، تنظیمات را پر کنید، و
          مستقیم از UI استقرار دهید.
        </p>
        <Link
          href="/discover/tools"
          className="inline-flex items-center gap-2 rounded-xl border border-white/15 bg-white/10 px-3 py-2 text-xs text-white/85 hover:bg-white/15"
        >
          🔎 پیشنهاد ابزار از Latent Box
        </Link>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-white/70">فیلتر بر اساس دسته‌بندی:</label>
        <select
          className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={categoryFilter}
          onChange={(event) => setCategoryFilter(event.target.value)}
        >
          {categories.map((cat) => (
            <option key={cat} value={cat}>
              {cat === "all" ? "همه" : cat}
            </option>
          ))}
        </select>
      </div>

      {loading && <p className="text-sm text-white/60">در حال بارگذاری کاتالوگ…</p>}
      {error && <p className="text-sm text-red-300">خطا: {error}</p>}

      <div className="grid gap-4 lg:grid-cols-2">
        {filtered.map((template) => (
          <div
            key={template.id}
            className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg transition hover:border-white/20"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase text-white/60">{template.category}</p>
                <h3 className="text-lg font-semibold text-white/90">{template.name}</h3>
                <p className="text-xs text-white/50">{template.framework}</p>
              </div>
              {template.icon && (
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/80">{template.icon}</span>
              )}
            </div>
            {template.description && (
              <p className="mt-3 text-sm leading-6 text-white/70">{template.description}</p>
            )}
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-white/70">
              {(template.capabilities || []).map((capability) => (
                <span
                  key={capability}
                  className="rounded-full border border-white/10 bg-white/5 px-3 py-1"
                >
                  {capability}
                </span>
              ))}
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-white/60">
              {(template.tags || []).map((tag) => (
                <span key={tag} className="rounded-md bg-white/10 px-2 py-1">#{tag}</span>
              ))}
            </div>
            <div className="mt-4 flex justify-end">
              <Link
                href={`/agents/catalog/${template.id}`}
                className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
              >
                تنظیم و استقرار
              </Link>
            </div>
          </div>
        ))}
        {!loading && !filtered.length && (
          <div className="rounded-2xl border border-dashed border-white/10 p-4 text-sm text-white/60">
            قالبی مطابق فیلترها پیدا نشد.
          </div>
        )}
      </div>
    </div>
  );
}
