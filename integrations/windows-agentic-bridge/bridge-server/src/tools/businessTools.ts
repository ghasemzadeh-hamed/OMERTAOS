import { Tool } from '@microsoft/ai-mcp-sdk';
import { OmertaClient } from '../omertaClient.js';

export function businessTools(client: OmertaClient): Tool[] {
  return [
    {
      name: 'omerta.run_agent_intent',
      description: 'High level wrapper to run an intent on an agent with parameters',
      inputSchema: {
        type: 'object',
        required: ['agent_id', 'intent'],
        properties: {
          agent_id: { type: 'string' },
          intent: { type: 'string' },
          params: { type: 'object' },
        },
      },
      async run(args) {
        const { agent_id, intent, params = {} } = args as { agent_id: string; intent: string; params?: Record<string, unknown> };
        return client.runTask(agent_id, intent, params || {});
      },
    },
    {
      name: 'omerta.search_memory',
      description: 'Search shared memory for relevant entries',
      inputSchema: {
        type: 'object',
        required: ['query'],
        properties: { query: { type: 'string' }, limit: { type: 'number' } },
      },
      async run(args) {
        const { query, limit = 10 } = args as { query: string; limit?: number };
        // placeholder for future gateway endpoint mapping
        return { query, limit, results: [] };
      },
    },
    {
      name: 'omerta.store_memory',
      description: 'Store a memory entry for later retrieval',
      inputSchema: {
        type: 'object',
        required: ['content'],
        properties: { content: { type: 'string' }, tags: { type: 'array', items: { type: 'string' } } },
      },
      async run(args) {
        const { content, tags = [] } = args as { content: string; tags?: string[] };
        return { stored: true, content, tags };
      },
    },
  ];
}
