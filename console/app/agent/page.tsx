"use client";

import { useState } from "react";

const CONTROL = process.env.NEXT_PUBLIC_GATEWAY_URL || "http://localhost:8080";
const TOKEN = process.env.NEXT_PUBLIC_AGENT_API_TOKEN || "";

export default function AgentPage() {
  const [goal, setGoal] = useState(
    "Create a sample task and show me the task board",
  );
  const [out, setOut] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${CONTROL}/agent/run`, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "x-agent-token": TOKEN,
        },
        body: JSON.stringify({ goal, context: { user: "admin" } }),
      });
      const data = await res.json();
      setOut(data);
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
      />
      <button
        onClick={run}
        className="mt-3 px-4 py-2 rounded-xl border"
        disabled={loading}
      >
        {loading ? "Running..." : "Run Agent"}
      </button>
      {out && (
        <pre className="mt-4 p-3 bg-gray-50 rounded overflow-auto">
          {JSON.stringify(out, null, 2)}
        </pre>
      )}
    </div>
  );
}
