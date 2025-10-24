'use client'

import * as Dialog from '@radix-ui/react-dialog'
import { useEffect, useState } from 'react'

const commands = [
  { label: 'Create Task', shortcut: 'T' },
  { label: 'Open Logs', shortcut: 'L' },
  { label: 'Switch Theme', shortcut: 'D' }
]

export function CommandPalette() {
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        setOpen((value) => !value)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur" />
        <Dialog.Content className="glass-panel fixed top-1/4 left-1/2 -translate-x-1/2 w-[420px] p-4 space-y-3">
          <Dialog.Title className="text-white/80 text-sm">Command Palette</Dialog.Title>
          <ul className="space-y-2 text-white/70 text-sm">
            {commands.map((command) => (
              <li key={command.label} className="flex justify-between glass-panel px-3 py-2">
                <span>{command.label}</span>
                <kbd className="text-xs bg-white/10 px-2 py-1 rounded">{command.shortcut}</kbd>
              </li>
            ))}
          </ul>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
