'use client';

import { motion } from 'framer-motion';

interface GlassCardProps {
  title: string;
  value: string;
  trend: string;
}

export function GlassCard({ title, value, trend }: GlassCardProps) {
  return (
    <motion.div
      className="glass-panel-dark p-6"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, type: 'spring' }}
    >
      <p className="text-sm uppercase tracking-[0.2em] text-slate-400">{title}</p>
      <div className="mt-4 flex items-end justify-between">
        <span className="text-3xl font-semibold">{value}</span>
        <span className="text-sm text-emerald-300">{trend}</span>
      </div>
    </motion.div>
  );
}
