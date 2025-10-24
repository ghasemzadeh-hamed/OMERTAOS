'use client'

import { motion } from 'framer-motion'
import { translate } from '../lib/i18n'
import { useUIStore } from '../lib/store'

interface ActivityItem {
  action: string
  created_at: string
  payload: Record<string, unknown>
}

const sample: ActivityItem[] = [
  { action: 'Task created', created_at: new Date().toISOString(), payload: { actor: 'admin' } },
  { action: 'Policy applied', created_at: new Date().toISOString(), payload: { rule: 'latency < 500ms' } }
]

export function ActivityFeed() {
  const { locale, rtl } = useUIStore()
  return (
    <section className={`glass-panel p-4 space-y-4 ${rtl ? 'rtl' : ''}`}>
      <h2 className="font-semibold text-white/80">{translate('activity', locale)}</h2>
      <div className="space-y-3">
        {sample.map((item, index) => (
          <motion.div key={index} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="glass-panel p-3">
            <p className="text-sm text-white/90">{item.action}</p>
            <p className="text-xs text-white/50">{new Date(item.created_at).toLocaleTimeString()}</p>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
