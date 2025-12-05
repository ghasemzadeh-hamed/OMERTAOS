import { describe, expect, it, vi } from 'vitest';
import { platformTools } from '../src/tools/platformTools.js';
import { OmertaClient } from '../src/omertaClient.js';

describe('platformTools', () => {
  it('exposes expected names', () => {
    const dummy = { listAgents: vi.fn(), getAgent: vi.fn(), runTask: vi.fn(), getTaskStatus: vi.fn(), getHealth: vi.fn() } as unknown as OmertaClient;
    const tools = platformTools(dummy);
    const names = tools.map((t) => t.name);
    expect(names).toContain('omerta.list_agents');
    expect(names).toContain('omerta.run_task');
  });
});
