'use client';

import { create } from 'zustand';

type TelemetryStatus = 'queued' | 'running' | 'completed' | 'failed';

interface TelemetryEvent {
  taskId: string;
  status: TelemetryStatus;
  timestamp: string;
  message?: string;
}

interface TelemetryState {
  events: TelemetryEvent[];
  addEvent: (event: TelemetryEvent) => void;
  clear: () => void;
}

export const useTelemetryStore = create<TelemetryState>((set) => ({
  events: [],
  addEvent: (event) => set((state) => ({ events: [event, ...state.events].slice(0, 25) })),
  clear: () => set({ events: [] })
}));
