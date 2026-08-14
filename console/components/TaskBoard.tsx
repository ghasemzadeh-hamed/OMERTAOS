'use client';

import { Task } from '../types';
import { TaskItem } from './TaskItem';
import { useMemo } from 'react';
import { motion } from 'framer-motion';

interface Props {
  tasks: Task[];
}

const columns: { key: string; title: string; statuses: Task['status'][] }[] = [
  { key: 'todo', title: 'To do', statuses: ['QUEUED'] },
  { key: 'doing', title: 'In progress', statuses: ['RUNNING'] },
  { key: 'done', title: 'Completed', statuses: ['COMPLETED'] },
  { key: 'failed', title: 'Failed', statuses: ['FAILED'] },
];

export function TaskBoard({ tasks }: Props) {
  const grouped = useMemo(() => {
    return columns.map((column) => ({
      ...column,
      tasks: tasks.filter((task) => column.statuses.includes(task.status)),
    }));
  }, [tasks]);

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {grouped.map((column, index) => (
        <motion.div
          key={column.key}
          className="glass-card flex flex-col gap-3 p-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05, type: 'spring', stiffness: 160, damping: 22 }}
        >
          <header className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-white">{column.title}</h4>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-200">
              {column.tasks.length}
            </span>
          </header>
          <div className="flex flex-1 flex-col gap-3">
            {column.tasks.length === 0 ? (
              <p className="text-xs text-slate-400">No tasks</p>
            ) : (
              column.tasks.map((task) => <TaskItem key={task.taskId} task={task} />)
            )}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
