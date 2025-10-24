'use client'

import { DashboardHeader } from '../components/dashboard-header'
import { TaskBoard } from '../components/task-board'
import { ActivityFeed } from '../components/activity-feed'
import { KPIChips } from '../components/kpi-chips'
import { useUIStore } from '../lib/store'
import { AuthPanel } from '../components/auth-panel'

export default function Page() {
  const { rtl } = useUIStore()
  return (
    <main className={`p-6 md:p-10 space-y-6 transition-all ${rtl ? 'rtl' : ''}`}>
      <DashboardHeader />
      <KPIChips />
      <div className="grid md:grid-cols-[1fr_320px] gap-6">
        <TaskBoard />
        <AuthPanel />
      </div>
      <ActivityFeed />
    </main>
  )
}
