import { OmertaClient } from '../omertaClient.js';
import { BridgeTool } from '../mcp/types.js';

export function adminTools(client: OmertaClient): BridgeTool[] {
  return [
    {
      name: 'omerta.restart_component',
      description: 'Request OMERTA component restart (guarded)',
      inputSchema: {
        type: 'object',
        required: ['component'],
        properties: { component: { type: 'string' } },
      },
      async run(args) {
        const { component } = args as { component: string };
        // Placeholder behavior until control API is available
        return { component, accepted: true };
      },
    },
    {
      name: 'omerta.get_metrics',
      description: 'Fetch metrics snapshot from control plane',
      inputSchema: { type: 'object', properties: {} },
      async run() {
        // Placeholder until metrics endpoint is available
        return { metrics: [], note: 'implement metrics mapping when endpoint is available' };
      },
    },
  ];
}
