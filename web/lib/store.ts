import { create } from 'zustand'
import { Locale } from './i18n'

interface UIState {
  locale: Locale
  rtl: boolean
  theme: 'light' | 'dark'
  setLocale: (locale: Locale) => void
  toggleRTL: () => void
  toggleTheme: () => void
}

export const useUIStore = create<UIState>((set) => ({
  locale: 'en',
  rtl: false,
  theme: 'dark',
  setLocale: (locale) => set({ locale }),
  toggleRTL: () => set((state) => ({ rtl: !state.rtl })),
  toggleTheme: () => set((state) => ({ theme: state.theme === 'dark' ? 'light' : 'dark' }))
}))
