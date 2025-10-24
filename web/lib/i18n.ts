export type Locale = 'en' | 'fa'

type Dictionary = Record<string, { en: string; fa: string }>

export const dictionary: Dictionary = {
  welcome: {
    en: 'Welcome to AION-OS',
    fa: 'به آيون خوش آمدید'
  },
  tasks: {
    en: 'Tasks',
    fa: 'کارها'
  },
  projects: {
    en: 'Projects',
    fa: 'پروژه‌ها'
  },
  health: {
    en: 'System Health',
    fa: 'وضعیت سیستم'
  },
  activity: {
    en: 'Recent Activity',
    fa: 'فعالیت اخیر'
  },
  createTask: {
    en: 'Create Task',
    fa: 'ایجاد کار'
  },
  rtl: {
    en: 'Switch RTL',
    fa: 'تغییر جهت'
  }
}

export function translate(key: keyof typeof dictionary, locale: Locale): string {
  return dictionary[key][locale]
}
