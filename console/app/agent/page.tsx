"use client";

import { useState } from "react";

export default function AgentPage() {
  const [goal, setGoal] = useState("");
  const [out, setOut] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!goal.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/proxy/tasks', {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          schemaVersion: '1.0',
          intent: 'agent_goal',
          params: { goal: goal.trim() },
          preferredEngine: 'auto',
          priority: 'normal',
          metadata: { source: 'console-agent-mode' },
        }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) throw new Error(data?.error ?? `Request failed with HTTP ${res.status}`);
      setOut(data);
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : 'Unable to run agent task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Agent Mode</h1>
      <textarea
        className="w-full border rounded p-2"
        rows={4}
        value={goal}
        onChange={(event) => setGoal(event.target.value)}
        placeholder="Describe the goal for the agent"
      />
      <button
        onClick={run}
        className="mt-3 px-4 py-2 rounded-xl border"
        disabled={loading || !goal.trim()}
      >
        {loading ? "Running..." : "Run Agent"}
      </button>
      {error && <p className="mt-3 text-sm text-rose-300">{error}</p>}
      {out !== null && (
        <pre className="mt-4 overflow-auto rounded bg-black/30 p-3 text-sm text-white/80">
          {JSON.stringify(out, null, 2)}
        </pre>
      )}
    </div>
  );
}
