"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:3000";
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

interface ToolRecommendation {
  id: string;
  name: string;
  category: string;
  url: string;
  description?: string;
  tags?: string[];
  source?: string;
}

interface AgentInstance {
  id: string;
  name: string;
  status: string;
}

function fieldLabel(key: string, schema: any) {
  const label = schema?.title || key;
  return schema?.description ? `${label} - ${schema.description}` : label;
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
  const [recommendedTools, setRecommendedTools] = useState<ToolRecommendation[]>([]);
  const [recommendationError, setRecommendationError] = useState<string | null>(null);

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

  useEffect(() => {
    if (!template) return;
    const scenario = (template.category || "").toLowerCase().replace(/\s+/g, "_");
    const params = new URLSearchParams();
    if (scenario) {
      params.set("scenario", scenario);
    }
    const headers: Record<string, string> = { accept: "application/json" };
    if (TENANT) {
      headers["tenant-id"] = TENANT;
    }
    fetch(`${CONTROL_BASE}/api/v1/recommendations/tools?${params.toString()}`, {
      credentials: "include",
      headers,
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text();
          throw new Error(text || "Failed to load recommendations");
        }
        return res.json();
      })
      .then((payload) => {
        setRecommendedTools(payload?.tools || []);
        setRecommendationError(null);
      })
      .catch((err) => setRecommendationError(err.message));
  }, [template]);

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
            <option value="">\u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u06cc\u062f</option>
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
    setStatus("\u062f\u0631 \u062d\u0627\u0644 \u0627\u06cc\u062c\u0627\u062f Agent...");
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
      setError(detail || "\u0627\u06cc\u062c\u0627\u062f Agent \u0646\u0627\u0645\u0648\u0641\u0642 \u0628\u0648\u062f");
      setStatus("");
      return;
    }
    const instance = (await res.json()) as AgentInstance;
    setCreated(instance);
    setStatus("Agent \u0627\u06cc\u062c\u0627\u062f \u0634\u062f\u061b \u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc\u062f Deploy \u06a9\u0646\u06cc\u062f.");
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
      setStatus("Agent \u0641\u0639\u0627\u0644 \u0634\u062f \u0648 \u0648\u0636\u0639\u06cc\u062a \u0628\u0647 \u0631\u0648\u0632 \u0634\u062f.");
    }
    setDeploying(false);
  };

  const properties = template?.config_schema?.properties || {};

  return (
    <div className="space-y-6 text-right">
      <div>
        <Link href="/agents/catalog" className="text-sm text-white/70 hover:text-white/90">
          \u2190 \u0628\u0627\u0632\u06af\u0634\u062a \u0628\u0647 \u06a9\u0627\u062a\u0627\u0644\u0648\u06af
        </Link>
        <h1 className="mt-2 text-2xl font-semibold text-white/90">{template?.name}</h1>
        <p className="text-sm text-white/65">{template?.description}</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 lg:col-span-2">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block space-y-1 md:col-span-2">
              <span className="text-sm text-white/80">\u0646\u0627\u0645 Agent</span>
              <input
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm"
                value={name}
                onChange={(event) => setName(event.target.value)}
              />
            </label>
            <label className="block space-y-1">
              <span className="text-sm text-white/80">\u062d\u0648\u0632\u0647 \u0627\u0633\u062a\u0642\u0631\u0627\u0631</span>
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
              <h3 className="text-sm font-semibold text-white/80">\u0627\u062a\u0635\u0627\u0644\u0627\u062a \u0648 \u062a\u0646\u0638\u06cc\u0645\u0627\u062a</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {Object.entries(properties).map(([key, schema]) => renderField(key, schema))}
                {!Object.keys(properties).length && (
                  <p className="text-sm text-white/60">\u0627\u06cc\u0646 \u0642\u0627\u0644\u0628 \u062a\u0646\u0638\u06cc\u0645\u0627\u062a \u0627\u0636\u0627\u0641\u06cc \u0646\u062f\u0627\u0631\u062f.</p>
                )}
              </div>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={submit}
              className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
            >
              \u0627\u06cc\u062c\u0627\u062f Agent
            </button>
            {created && (
              <button
                onClick={deploy}
                disabled={deploying}
                className="rounded-xl border border-emerald-400/40 bg-emerald-500/20 px-4 py-2 text-sm text-emerald-100 transition hover:bg-emerald-500/30"
              >
                {deploying ? "\u062f\u0631 \u062d\u0627\u0644 \u0641\u0639\u0627\u0644\u200c\u0633\u0627\u0632\u06cc..." : "Deploy"}
              </button>
            )}
            {status && <span className="text-sm text-white/70">{status}</span>}
            {error && <span className="text-sm text-red-300">{error}</span>}
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-white/80">Recipe</h3>
          <pre className="max-h-72 overflow-auto rounded-xl bg-black/30 p-3 text-xs text-white/80">
            {JSON.stringify(recipe, null, 2)}
          </pre>

          <div className="mt-4 space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-semibold text-white/80">\u067e\u06cc\u0634\u0646\u0647\u0627\u062f \u0627\u0628\u0632\u0627\u0631 (Latent Box)</h4>
              <Link
                href="/discover/tools"
                className="text-xs text-sky-200 hover:text-white"
              >
                \u0645\u0634\u0627\u0647\u062f\u0647 \u0647\u0645\u0647
              </Link>
            </div>
            {recommendationError && <p className="text-xs text-red-300">{recommendationError}</p>}
            <div className="space-y-2 max-h-64 overflow-auto pr-1">
              {recommendedTools.map((tool) => (
                <div
                  key={tool.id}
                  className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white/70"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <p className="text-[11px] uppercase text-white/50">{tool.category}</p>
                      <p className="text-sm text-white/85">{tool.name}</p>
                    </div>
                    <a
                      href={tool.url}
                      className="rounded-lg border border-white/15 px-2 py-1 text-[11px] text-white/80 hover:bg-white/15"
                      target="_blank"
                      rel="noreferrer"
                    >
                      \u0644\u06cc\u0646\u06a9
                    </a>
                  </div>
                  <div className="mt-1 flex flex-wrap gap-1 text-[11px] text-white/60">
                    {(tool.tags || []).slice(0, 4).map((tag) => (
                      <span key={tag} className="rounded bg-white/10 px-2 py-0.5">#{tag}</span>
                    ))}
                  </div>
                </div>
              ))}
              {!recommendedTools.length && !recommendationError && (
                <p className="text-xs text-white/60">\u067e\u06cc\u0634\u0646\u0647\u0627\u062f \u0641\u0639\u0627\u0644\u06cc \u0645\u0648\u062c\u0648\u062f \u0646\u06cc\u0633\u062a.</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {created && (
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <h3 className="text-sm font-semibold text-white/80">Agent \u0627\u06cc\u062c\u0627\u062f \u0634\u062f\u0647</h3>
          <p className="text-sm text-white/70">ID: {created.id}</p>
          <p className="text-sm text-white/70">Status: {created.status}</p>
        </div>
      )}
    </div>
  );
}
