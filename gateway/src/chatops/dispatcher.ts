import { randomUUID } from 'node:crypto';
import { deliverEvent } from '../webhooks/outbound.js';

export interface CommandContext {
  actor: string;
  tenant?: string;
}

export interface ChatExecution {
  sessionId: string;
  events: Array<{ type: string; data: unknown }>;
}

export const orchestrateCommand = async (command: string, context: CommandContext): Promise<ChatExecution> => {
  const sessionId = randomUUID();
  const metadata = new Metadata();
  if (context.tenant) {
    metadata.add('x-tenant', context.tenant);
  }
  const events: ChatExecution['events'] = [];
  if (command.startsWith('/install agent')) {
    const [, , image] = command.split(' ');
    events.push({ type: 'info', data: `Installing module ${image}` });
    await deliverEvent('module.install.requested', { image, sessionId, actor: context.actor });
  } else if (command.startsWith('/kernel')) {
    events.push({ type: 'info', data: 'Kernel command received' });
    await deliverEvent('kernel.command', { command, sessionId });
  } else if (command.startsWith('/memory')) {
    events.push({ type: 'info', data: 'Memory operation scheduled' });
    await deliverEvent('memory.command', { command, sessionId });
  } else {
    events.push({ type: 'error', data: `Unknown command ${command}` });
  }
  return { sessionId, events };
};
