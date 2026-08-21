"use client";

import { useCallback, useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

type ModelEntry = {
  name?: string;
  provider?: string;
  profile?: string;
  path?: string;
  size?: number;
};

function normalizeModels(payload: unknown): ModelEntry[] {
  if (Array.isArray(payload)) {
    return payload.filter(
      (item): item is ModelEntry => Boolean(item) && typeof item === "object",
    );
  }
  if (!payload || typeof payload !== "object") return [];
  const source = payload as Record<string, unknown>;
  for (const key of ["models", "items", "local"]) {
    const value = source[key];
    if (Array.isArray(value)) {
      return value.filter(
        (item): item is ModelEntry => Boolean(item) && typeof item === "object",
      );
    }
  }
  return [];
}

export default function ModelsPage() {
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/system/models", { cache: "no-store" });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        throw new Error(
          payload?.error || `Request failed with HTTP ${response.status}`,
        );
      }
      setModels(normalizeModels(payload));
    } catch (loadError) {
      setModels([]);
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unable to load models",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="space-y-5 text-left">
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-white/10 pb-4">
        <div>
          <h2 className="text-2xl font-semibold text-white/90">Models</h2>
          <p className="mt-1 text-sm text-white/60">
            Models reported by the Gateway and canonical Control registry.
          </p>
        </div>
        <Button
          type="button"
          variant="outline"
          onClick={() => void load()}
          disabled={loading}
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
      {!loading && !error && models.length === 0 ? (
        <p className="border border-dashed border-white/15 p-5 text-sm text-white/60">
          No models are currently reported.
        </p>
      ) : null}

      <div className="overflow-x-auto border border-white/10">
        <table className="min-w-full divide-y divide-white/10 text-sm">
          <thead className="bg-white/5 text-left text-white/60">
            <tr>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Provider</th>
              <th className="px-4 py-3 font-medium">Profile</th>
              <th className="px-4 py-3 font-medium">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {models.map((model, index) => (
              <tr key={`${model.name ?? "model"}-${model.path ?? index}`}>
                <td className="px-4 py-3 font-medium text-white/85">
                  {model.name || "Unnamed model"}
                </td>
                <td className="px-4 py-3 text-white/65">
                  {model.provider || "Not reported"}
                </td>
                <td className="px-4 py-3 text-white/65">
                  {model.profile || "Not reported"}
                </td>
                <td className="max-w-sm truncate px-4 py-3 text-white/50">
                  {model.path || "Gateway registry"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="border border-amber-400/25 bg-amber-400/10 p-3 text-sm text-amber-100">
        Install and remove actions remain hidden because the running Gateway
        exposes model discovery only.
      </p>
    </div>
  );
}
