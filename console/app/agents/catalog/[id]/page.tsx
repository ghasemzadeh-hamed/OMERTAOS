"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || "http://localhost:8000";
const TENANT = process.env.NEXT_PUBLIC_TENANT_ID;

interface AgentTemplate {
  id: string;
  name: string;
  category: string;
  framework: string;
  description?: string;
  config_schema?: {
    properties?: Record<string, any>;
    required?: string[];
  };
}

interface AgentTemplateResponse {
  template: AgentTemplate;
  recipe: Record<string, any>;
}

interface AgentInstance {
  id: string;
  name: string;
  status: string;
}

function fieldLabel(key: string, schema: any) {
  const label = schema?.title || key;
  return schema?.description ? `${label} — ${schema.description}` : label;
}

export default function AgentTemplateWizardPage() {
  const params = useParams();
  const templateId = Array.isArray(params?.id) ? params.id[0] : (params?.id as string);
  const [template, setTemplate] = useState<AgentTemplate | null>(null);
  const [recipe, setRecipe] = useState<Record<string, any>>({});
  const [config, setConfig] = useState<Record<string, any>>({});
  const [name, setName] = useState<string>("");
  const [scope, setScope] = useState<string>("tenant");
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<AgentInstance | null>(null);
  const [deploying, setDeploying] = useState<boolean>(false);

  const requiredFields = useMemo(
    () => new Set(template?.config_schema?.required || []),
    [template?.config_schema?.required],
  );

  useEffect(() => {
    if (!templateId) return;
    const headers: Record<string, string> = { accept: "application/json" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    fetch(`${CONTROL_BASE}/api/agent-catalog/${templateId}`, { credentials: "include", headers })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || "Failed to load template");
        }
        return res.json();
      })
      .then((data: AgentTemplateResponse) => {
        setTemplate(data.template);
        setRecipe(data.recipe || {});
        setName(data.template?.name || "");
      })
      .catch((err) => {
        setError(err.message);
      });
  }, [templateId]);

  const handleFieldChange = (key: string, value: any) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  const renderField = (key: string, schema: any) => {
    const type = schema?.type;
    const isRequired = requiredFields.has(key);
    if (schema?.enum) {
      return (
        <label key={key} className="block space-y-1">
          <span className="text-sm text-white/80">
            {fieldLabel(key, schema)} {isRequired && <span className="text-red-300">*</span>}
          </span>
          <select
            className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
            value={config[key] ?? ""}
            onChange={(event) => handleFieldChange(key, event.target.value)}
          >
            <option value="">انتخاب کنید</option>
            {schema.enum.map((option: string) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
      );
    }
    const inputType = schema?.format === "secret" ? "password" : type === "number" ? "number" : "text";
    return (
      <label key={key} className="block space-y-1">
        <span className="text-sm text-white/80">
          {fieldLabel(key, schema)} {isRequired && <span className="text-red-300">*</span>}
        </span>
        <input
          type={inputType}
          className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
          value={config[key] ?? ""}
          onChange={(event) => handleFieldChange(key, inputType === "number" ? Number(event.target.value) : event.target.value)}
          placeholder={schema?.placeholder || ""}
        />
      </label>
    );
  };

  const submit = async () => {
    if (!template) return;
    setError(null);
    setStatus("در حال ایجاد Agent…");
    const headers: Record<string, string> = { "content-type": "application/json" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    const res = await fetch(`${CONTROL_BASE}/api/agents`, {
      method: "POST",
      credentials: "include",
      headers,
      body: JSON.stringify({
        template_id: template.id,
        name,
        config,
        scope,
        enabled: true,
      }),
    });
    if (!res.ok) {
      const detail = await res.text();
      setError(detail || "ایجاد Agent ناموفق بود");
      setStatus("");
      return;
    }
    const instance = (await res.json()) as AgentInstance;
    setCreated(instance);
    setStatus("Agent ایجاد شد؛ می‌توانید Deploy کنید.");
  };

  const deploy = async () => {
    if (!created) return;
    setDeploying(true);
    const headers: Record<string, string> = { "content-type": "application/json" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    const res = await fetch(`${CONTROL_BASE}/api/agents/${created.id}/deploy`, {
      method: "POST",
      credentials: "include",
      headers,
    });
    if (!res.ok) {
      const detail = await res.text();
      setError(detail || "Deployment failed");
    } else {
      const payload = (await res.json()) as AgentInstance;
      setCreated(payload);
      setStatus("Agent فعال شد و وضعیت به روز شد.");
    }
    setDeploying(false);
  };

  const properties = template?.config_schema?.properties || {};

  return (
    <div className="space-y-6 text-right">
      <div>
        <Link href="/agents/catalog" className="text-sm text-white/70 hover:text-white/90">
          ← بازگشت به کاتالوگ
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-white/90">{template?.name}</h1>
        <p className="text-sm text-white/65">{template?.description}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block space-y-1 md:col-span-2">
              <span className="text-sm text-white/80">نام Agent</span>
              <input
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label className="block space-y-1">
              <span className="text-sm text-white/80">حوزه استقرار</span>
              <select
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
                value={scope}
                onChange={(event) => setScope(event.target.value)}
              >
                <option value="tenant">Tenant</option>
                <option value="user">User</option>
              </select>
            </label>
            <div className="md:col-span-2 space-y-3">
              <h3 className="text-sm font-semibold text-white/80">اتصالات و تنظیمات</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {Object.entries(properties).map(([key, schema]) => renderField(key, schema))}
                {!Object.keys(properties).length && (
                  <p className="text-sm text-white/60">این قالب تنظیمات اضافی ندارد.</p>
                )}
              </div>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={submit}
              className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
            >
              ایجاد Agent
            </button>
            {created && (
              <button
                onClick={deploy}
                disabled={deploying}
                className="rounded-xl border border-emerald-400/40 bg-emerald-500/20 px-4 py-2 text-sm text-emerald-100 transition hover:bg-emerald-500/30"
              >
                {deploying ? "در حال فعال‌سازی…" : "Deploy"}
              </button>
            )}
            {status && <span className="text-sm text-white/70">{status}</span>}
            {error && <span className="text-sm text-red-300">{error}</span>}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-white/80">Recipe</h3>
          <pre className="max-h-96 overflow-auto rounded-xl bg-black/30 p-3 text-xs text-white/80">
            {JSON.stringify(recipe, null, 2)}
          </pre>
        </div>
      </div>

      {created && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <h3 className="text-sm font-semibold text-white/80">Agent ایجاد شده</h3>
          <p className="text-sm text-white/70">ID: {created.id}</p>
          <p className="text-sm text-white/70">Status: {created.status}</p>
        </div>
      )}
    </div>
  );
}
