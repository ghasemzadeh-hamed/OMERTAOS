'use client'

import { motion } from 'framer-motion'

const kpis = [
  { label: 'Latency', value: '420ms' },
  { label: 'Throughput', value: '320 req/min' },
  { label: 'Success', value: '99.2%' }
]

export function KPIChips() {
  return (
    <div className="flex flex-wrap gap-3">
      {kpis.map((kpi) => (
        <motion.div
          key={kpi.label}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel px-4 py-2 text-xs uppercase tracking-wide text-white/80"
        >
          <span className="block text-[11px] text-white/60">{kpi.label}</span>
          <span className="text-sm font-semibold">{kpi.value}</span>
        </motion.div>
      ))}
    </div>
  )
}
