"use client";

import { useCallback, useEffect, useState } from "react";
import { Check, RefreshCcw, RotateCcw, Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type RouterConfiguration = {
  mode: "auto" | "local" | "api";
  local_provider: string | null;
  api_provider: string | null;
};

type ConfigurationStatus = {
  effective: { router: RouterConfiguration };
  proposed: { router: RouterConfiguration } | null;
  has_pending: boolean;
  can_revert: boolean;
  updated_at: string;
};

const emptyRouter: RouterConfiguration = {
  mode: "auto",
  local_provider: null,
  api_provider: null,
};

async function configurationRequest(
  path: string,
  init?: RequestInit,
): Promise<ConfigurationStatus> {
  const response = await fetch(`/api/system/admin/config/${path}`, {
    ...init,
    cache: "no-store",
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      payload?.details?.detail || payload?.details || payload?.error;
    throw new Error(
      typeof detail === "string"
        ? detail
        : `Request failed with HTTP ${response.status}`,
    );
  }
  return payload as ConfigurationStatus;
}

export default function ConfigCenterPage() {
  const [remote, setRemote] = useState<ConfigurationStatus | null>(null);
  const [draft, setDraft] = useState<RouterConfiguration>(emptyRouter);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const acceptStatus = useCallback((status: ConfigurationStatus) => {
    setRemote(status);
    setDraft(
      status.proposed?.router ?? status.effective?.router ?? emptyRouter,
    );
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      acceptStatus(await configurationRequest("status"));
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unable to load configuration",
      );
    } finally {
      setLoading(false);
    }
  }, [acceptStatus]);

  useEffect(() => {
    void load();
  }, [load]);

  const run = async (action: "propose" | "apply" | "revert") => {
    setBusy(true);
    setMessage(null);
    setError(null);
    try {
      const status = await configurationRequest(action, {
        method: "POST",
        body: JSON.stringify(action === "propose" ? { router: draft } : {}),
      });
      acceptStatus(status);
      setMessage(
        action === "propose"
          ? "Draft saved. Apply it to make the policy effective."
          : action === "apply"
            ? "Policy applied."
            : "Last pending or applied change reverted.",
      );
    } catch (actionError) {
      setError(
        actionError instanceof Error
          ? actionError.message
          : "Configuration action failed",
      );
    } finally {
      setBusy(false);
    }
  };

  const update = (field: keyof RouterConfiguration, value: string | null) => {
    setDraft((current) => ({ ...current, [field]: value || null }));
  };

  return (
    <div className="space-y-6 text-left">
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-white/10 pb-4">
        <div>
          <h2 className="text-2xl font-semibold text-white/90">
            Routing policy
          </h2>
          <p className="mt-1 text-sm text-white/60">
            Propose, review, apply, or revert the Control-owned router
            configuration.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={() => void load()}
          disabled={loading || busy}
        >
          <RefreshCcw
            className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </header>

      {error ? (
        <p className="border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-200">
          {error}
        </p>
      ) : null}
      {message ? (
        <p className="border border-emerald-400/30 bg-emerald-400/10 p-3 text-sm text-emerald-100">
          {message}
        </p>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <label className="space-y-1 text-sm text-white/70">
          <span>Routing mode</span>
          <select
            aria-label="Routing mode"
            value={draft.mode}
            onChange={(event) => update("mode", event.target.value)}
            className="h-10 w-full rounded-md border border-white/15 bg-slate-950 px-3 text-white"
            disabled={loading || busy || !remote}
          >
            <option value="auto">auto</option>
            <option value="local">local</option>
            <option value="api">api</option>
          </select>
        </label>
        <label className="space-y-1 text-sm text-white/70">
          <span>Local provider</span>
          <Input
            aria-label="Local provider"
            value={draft.local_provider ?? ""}
            onChange={(event) => update("local_provider", event.target.value)}
            placeholder="Not configured"
            disabled={loading || busy || !remote}
          />
        </label>
        <label className="space-y-1 text-sm text-white/70">
          <span>API provider</span>
          <Input
            aria-label="API provider"
            value={draft.api_provider ?? ""}
            onChange={(event) => update("api_provider", event.target.value)}
            placeholder="Not configured"
            disabled={loading || busy || !remote}
          />
        </label>
      </section>

      <div className="flex flex-wrap gap-2">
        <Button
          type="button"
          variant="secondary"
          onClick={() => void run("propose")}
          disabled={loading || busy || !remote}
        >
          <Save className="mr-2 h-4 w-4" /> Save draft
        </Button>
        <Button
          type="button"
          onClick={() => void run("apply")}
          disabled={loading || busy || !remote?.has_pending}
        >
          <Check className="mr-2 h-4 w-4" /> Apply
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => void run("revert")}
          disabled={
            loading || busy || (!remote?.has_pending && !remote?.can_revert)
          }
        >
          <RotateCcw className="mr-2 h-4 w-4" /> Revert
        </Button>
      </div>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="border border-white/10 bg-white/5 p-4">
          <h3 className="text-sm font-semibold text-white/85">Effective</h3>
          <pre className="mt-3 overflow-auto text-xs leading-6 text-emerald-100">
            {JSON.stringify(remote?.effective ?? {}, null, 2)}
          </pre>
        </div>
        <div className="border border-white/10 bg-white/5 p-4">
          <h3 className="text-sm font-semibold text-white/85">
            Pending proposal
          </h3>
          <pre className="mt-3 overflow-auto text-xs leading-6 text-amber-100">
            {JSON.stringify(remote?.proposed ?? null, null, 2)}
          </pre>
        </div>
      </section>

      {remote?.updated_at ? (
        <p className="text-xs text-white/45">
          Last persisted update: {new Date(remote.updated_at).toLocaleString()}
        </p>
      ) : null}
    </div>
  );
}
