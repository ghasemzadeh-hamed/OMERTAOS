'use client';

import { Task } from '../types';
import { motion } from 'framer-motion';

interface Props {
  task: Task;
}

export function TaskItem({ task }: Props) {
  return (
    <motion.div
      layout
      className="glass-card space-y-2 p-4 text-sm"
      initial={{ opacity: 0.5, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: 'spring', stiffness: 220, damping: 18 }}
    >
      <div className="flex items-center justify-between">
        <span className="font-medium text-white">{task.intent}</span>
        <span className="rounded-full bg-white/15 px-3 py-1 text-xs uppercase tracking-wide text-white">
          {task.status}
        </span>
      </div>
      <pre className="rounded-lg bg-black/30 p-3 text-xs text-slate-300">
        {JSON.stringify(task.params, null, 2)}
      </pre>
      {task.result ? (
        <details className="rounded-lg bg-black/20 p-3">
          <summary className="cursor-pointer text-xs font-semibold text-slate-200">Result</summary>
          <pre className="mt-2 text-xs text-slate-300">{JSON.stringify(task.result, null, 2)}</pre>
        </details>
      ) : null}
    </motion.div>
  );
}
