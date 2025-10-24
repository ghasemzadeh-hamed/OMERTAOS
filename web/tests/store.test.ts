import { describe, it, expect } from 'vitest'
import { useUIStore } from '../lib/store'

describe('UI store', () => {
  it('toggles theme', () => {
    const initial = useUIStore.getState().theme
    useUIStore.getState().toggleTheme()
    expect(useUIStore.getState().theme).not.toBe(initial)
  })
})
