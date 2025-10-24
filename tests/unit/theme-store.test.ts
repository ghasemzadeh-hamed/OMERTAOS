import { describe, expect, it } from 'vitest';
import { act } from 'react';
import { useThemeStore } from '@/lib/stores/theme-store';

describe('theme store', () => {
  it('toggles direction', () => {
    const initial = useThemeStore.getState().direction;
    act(() => useThemeStore.getState().toggle());
    expect(useThemeStore.getState().direction).not.toEqual(initial);
  });
});
