import { create } from 'zustand';

interface UIState {
  commandPaletteOpen: boolean;
  role: string;
  openCommandPalette: () => void;
  closeCommandPalette: () => void;
  toggleCommandPalette: () => void;
  setRole: (role: string) => void;
}

export const useUIStore = create<UIState>((set) => ({
  commandPaletteOpen: false,
  role: 'operator',
  openCommandPalette: () => set({ commandPaletteOpen: true }),
  closeCommandPalette: () => set({ commandPaletteOpen: false }),
  toggleCommandPalette: () => set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
  setRole: (role) => set({ role }),
}));
