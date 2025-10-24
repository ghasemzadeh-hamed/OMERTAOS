'use client'

import { motion } from 'framer-motion'
import { Moon, Sun, Languages, Compass } from 'lucide-react'
import { translate } from '../lib/i18n'
import { useUIStore } from '../lib/store'

export function DashboardHeader() {
  const { theme, toggleTheme, locale, setLocale, rtl, toggleRTL } = useUIStore()
  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glass-panel p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-6 ${rtl ? 'rtl' : ''}`}
    >
      <div>
        <div className="flex items-center gap-3">
          <div className="h-12 w-12 rounded-full bg-gradient-to-br from-sky-400/80 to-indigo-500/80 flex items-center justify-center animate-pulse-glow">
            <Compass className="text-white" />
          </div>
          <div>
            <p className="text-sm uppercase tracking-widest text-white/70">AION-OS</p>
            <h1 className="text-2xl font-semibold text-white drop-shadow">{translate('welcome', locale)}</h1>
          </div>
        </div>
      </div>
      <div className="flex gap-3">
        <button
          aria-label="Toggle theme"
          className="glass-panel px-4 py-2 flex items-center gap-2 text-sm"
          onClick={() => {
            toggleTheme()
            document.documentElement.dataset.theme = theme === 'dark' ? 'light' : 'dark'
          }}
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          <span>{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>
        <button
          aria-label="Toggle locale"
          className="glass-panel px-4 py-2 flex items-center gap-2 text-sm"
          onClick={() => setLocale(locale === 'en' ? 'fa' : 'en')}
        >
          <Languages size={16} />
          <span>{locale === 'en' ? 'FA' : 'EN'}</span>
        </button>
        <button
          aria-label="Toggle RTL"
          className="glass-panel px-4 py-2 text-sm"
          onClick={() => toggleRTL()}
        >
          {translate('rtl', locale)}
        </button>
      </div>
    </motion.header>
  )
}
