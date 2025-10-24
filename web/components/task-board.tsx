'use client'

import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { useEffect } from 'react'
import { translate } from '../lib/i18n'
import { useUIStore } from '../lib/store'

interface Task {
  id: number
  intent: string
  status: string
  priority: number
  created_at: string
}

const columns: { key: string; title: string }[] = [
  { key: 'queued', title: 'Queued' },
  { key: 'running', title: 'Running' },
  { key: 'completed', title: 'Completed' },
  { key: 'failed', title: 'Failed' }
]

async function fetchTasks(): Promise<Task[]> {
  const token = window.localStorage.getItem('aion-token')
  const res = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080'}/tasks`, {
    headers: {
      Authorization: token ? `Bearer ${token}` : ''
    }
  })
  if (!res.ok) {
    return []
  }
  return await res.json()
}

export function TaskBoard() {
  const { locale, rtl } = useUIStore()
  const { data, refetch } = useQuery({ queryKey: ['tasks'], queryFn: fetchTasks })

  useEffect(() => {
    const token = window.localStorage.getItem('aion-token')
    const url = new URL(`${process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'http://localhost:8080'}/events/tasks`)
    if (token) {
      url.searchParams.set('token', token)
    }
    const events = new EventSource(url.toString())
    events.onmessage = () => {
      refetch()
    }
    return () => events.close()
  }, [refetch])

  return (
    <section className={`grid md:grid-cols-4 gap-6 ${rtl ? 'rtl' : ''}`}>
      {columns.map((column) => (
        <motion.div
          key={column.key}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel p-4 space-y-3"
        >
          <h2 className="font-semibold tracking-wide text-white/80">{translate('tasks', locale)} — {column.title}</h2>
          <div className="space-y-3">
            {data?.filter((task) => task.status === column.key).map((task) => (
              <motion.div
                key={task.id}
                layout
                className="glass-panel border border-white/10 p-3"
              >
                <p className="text-sm text-white/90">{task.intent}</p>
                <p className="text-xs text-white/50">Priority {task.priority}</p>
              </motion.div>
            )) || <p className="text-xs text-white/50">No tasks</p>}
          </div>
        </motion.div>
      ))}
    </section>
  )
}
