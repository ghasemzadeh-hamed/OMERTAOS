import { FastifyInstance } from 'fastify';
import { TelemetryEvent } from './types.js';

export class TelemetryBroker {
  private listeners: Map<string, Set<(event: TelemetryEvent) => void>> = new Map();

  subscribe(taskId: string, listener: (event: TelemetryEvent) => void): () => void {
    const set = this.listeners.get(taskId) ?? new Set();
    set.add(listener);
    this.listeners.set(taskId, set);
    return () => {
      set.delete(listener);
      if (!set.size) {
        this.listeners.delete(taskId);
      }
    };
  }

  publish(event: TelemetryEvent) {
    const listeners = this.listeners.get(event.taskId);
    if (!listeners) {
      return;
    }
    for (const listener of listeners) {
      listener(event);
    }
  }
}

export const registerTelemetry = (app: FastifyInstance) => {
  const broker = new TelemetryBroker();
  app.decorate('telemetry', broker);
};

declare module 'fastify' {
  interface FastifyInstance {
    telemetry: TelemetryBroker;
  }
}
