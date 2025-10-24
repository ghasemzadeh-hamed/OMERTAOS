'use client';

import { create } from 'zustand';

type Direction = 'ltr' | 'rtl';

type State = {
  direction: Direction;
  toggle: () => void;
  setDirection: (dir: Direction) => void;
};

export const useThemeStore = create<State>((set) => ({
  direction: 'ltr',
  toggle: () =>
    set((state) => ({
      direction: state.direction === 'ltr' ? 'rtl' : 'ltr'
    })),
  setDirection: (dir) => set({ direction: dir })
}));
