'use client';

import { motion } from 'framer-motion';
import { useMemo } from 'react';

const entries = [
  { id: 1, actor: 'Nima', action: 'deployed summarize_text module', time: '2m ago' },
  { id: 2, actor: 'Ava', action: 'routed task AION-482 via local engine', time: '12m ago' },
  { id: 3, actor: 'Control Plane', action: 'synced Qdrant vector index', time: '32m ago' }
];

export function ActivityFeed() {
  const items = useMemo(() => entries, []);
  return (
    <motion.div
      className="glass-panel-dark h-full space-y-4 p-6"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <header>
        <h2 className="text-xl font-semibold text-white">Live activity</h2>
        <p className="text-sm text-slate-400">Streaming telemetry events from the gateway.</p>
      </header>
      <ul className="space-y-3">
        {items.map((item) => (
          <li key={item.id} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
            <p className="text-sm text-slate-200">
              <span className="font-semibold text-white">{item.actor}</span> {item.action}
            </p>
            <p className="text-xs uppercase tracking-wide text-slate-400">{item.time}</p>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}
