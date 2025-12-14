import { Tool } from '@microsoft/ai-mcp-sdk';
import { OmertaClient } from '../omertaClient.js';
import { getAgentInput, runTaskInput, taskStatusInput } from '../mcp/schemas.js';

export function platformTools(client: OmertaClient): Tool[] {
  return [
    {
      name: 'omerta.list_agents',
      description: 'List available OMERTA agents',
      inputSchema: {
        type: 'object',
        properties: {},
      },
      async run() {
        const agents = await client.listAgents();
        return { agents };
      },
    },
    {
      name: 'omerta.get_agent',
      description: 'Get metadata for an OMERTA agent',
      inputSchema: {
        type: 'object',
        required: ['agent_id'],
        properties: { agent_id: { type: 'string' } },
      },
      async run(args) {
        const parsed = getAgentInput.parse(args);
        return client.getAgent(parsed.agent_id);
      },
    },
    {
      name: 'omerta.run_task',
      description: 'Run a task on an OMERTA agent',
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
        const parsed = runTaskInput.parse(args);
        return client.runTask(parsed.agent_id, parsed.intent, parsed.params);
      },
    },
    {
      name: 'omerta.get_task_status',
      description: 'Fetch the status for a previously created task',
      inputSchema: {
        type: 'object',
        required: ['task_id'],
        properties: { task_id: { type: 'string' } },
      },
      async run(args) {
        const parsed = taskStatusInput.parse(args);
        return client.getTaskStatus(parsed.task_id);
      },
    },
    {
      name: 'omerta.get_health',
      description: 'Check gateway and control plane health',
      inputSchema: { type: 'object', properties: {} },
      async run() {
        return client.getHealth();
      },
    },
  ];
}
