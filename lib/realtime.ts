import { EventEmitter } from 'events';

const emitter = new EventEmitter();

export function publishTaskUpdate(payload: unknown) {
  emitter.emit('task:update', payload);
}

export function subscribeTaskUpdates(cb: (payload: unknown) => void) {
  emitter.on('task:update', cb);
  return () => emitter.off('task:update', cb);
}
