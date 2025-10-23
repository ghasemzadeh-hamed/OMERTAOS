'use client';

import { motion } from 'framer-motion';
import { useMemo } from 'react';
import { useLocale } from '../../lib/use-locale';

const tasks = [
  { id: 'AION-101', title: 'Summarize research note', status: 'todo', assignee: 'Ava', priority: 'high' },
  { id: 'AION-102', title: 'Ingest telemetry dataset', status: 'doing', assignee: 'Nima', priority: 'medium' },
  { id: 'AION-103', title: 'Validate hybrid routing', status: 'done', assignee: 'Lina', priority: 'high' }
];

const columnOrder = ['todo', 'doing', 'done'] as const;

export function TaskBoard() {
  const grouped = useMemo(() => {
    return columnOrder.map((status) => ({
      status,
      items: tasks.filter((task) => task.status === status)
    }));
  }, []);
  const { t } = useLocale();

  return (
    <div className="grid gap-4 md:grid-cols-3">
      {grouped.map((column) => (
        <motion.div
          key={column.status}
          className="glass-panel-dark space-y-4 p-6"
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
        >
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold capitalize">{t(`tasks.status.${column.status}`)}</h3>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-wide text-slate-200">
              {column.items.length}
            </span>
          </div>
          <ul className="space-y-3">
            {column.items.map((task) => (
              <li key={task.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm text-slate-300">{task.id}</p>
                <h4 className="text-lg font-semibold text-white">{task.title}</h4>
                <div className="mt-3 flex items-center justify-between text-xs uppercase tracking-wide text-slate-400">
                  <span>{t('tasks.assignee', { name: task.assignee })}</span>
                  <span className="rounded-full bg-accent/30 px-2 py-1 text-white">{task.priority}</span>
                </div>
              </li>
            ))}
          </ul>
        </motion.div>
      ))}
    </div>
  );
}
