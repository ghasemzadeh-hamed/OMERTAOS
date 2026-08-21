"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, RefreshCcw } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function RunDetailsPage() {
  const params = useParams<{ taskId: string }>();
  const taskId = params?.taskId ?? "";
  const [task, setTask] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!taskId) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `/api/system/tasks/${encodeURIComponent(taskId)}`,
        { cache: "no-store" },
      );
      const payload = await response.json().catch(() => null);
      if (!response.ok)
        throw new Error(
          payload?.error || `Request failed with HTTP ${response.status}`,
        );
      setTask(payload);
    } catch (loadError) {
      setTask(null);
      setError(
        loadError instanceof Error ? loadError.message : "Unable to load task",
      );
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="min-h-dvh bg-slate-950 px-4 py-8 text-white">
      <div className="mx-auto max-w-4xl space-y-5">
        <header className="flex flex-wrap items-start justify-between gap-3 border-b border-white/10 pb-4">
          <div>
            <p className="text-xs uppercase text-white/45">Task run</p>
            <h1 className="mt-1 break-all text-xl font-semibold">{taskId}</h1>
          </div>
          <div className="flex gap-2">
            <Button asChild variant="outline">
              <Link href="/chat">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Chat
              </Link>
            </Button>
            <Button
              type="button"
              onClick={() => void load()}
              disabled={loading}
            >
              <RefreshCcw
                className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`}
              />
              Refresh
            </Button>
          </div>
        </header>
        {error ? (
          <p className="border border-rose-400/30 bg-rose-400/10 p-3 text-sm text-rose-200">
            {error}
          </p>
        ) : null}
        <pre className="max-h-[70vh] overflow-auto border border-white/10 bg-black/30 p-4 text-xs leading-6 text-emerald-100">
          {JSON.stringify(task, null, 2)}
        </pre>
      </div>
    </main>
  );
}
