import Ajv from 'ajv';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { Logger } from '../logger.js';
import { OmertaClient } from '../omertaClient.js';
import { platformTools } from '../tools/platformTools.js';
import { businessTools } from '../tools/businessTools.js';
import { adminTools } from '../tools/adminTools.js';

export function buildServer(client: OmertaClient, logger: Logger) {
  const server = new Server(
    { name: 'omertaos-wsl-bridge', version: '0.1.0' },
    { capabilities: { tools: {} } },
  );
  const tools = [...platformTools(client), ...businessTools(client), ...adminTools(client)];
  const validators = new Map(
    tools.map((tool) => [tool.name, new Ajv({ allErrors: true }).compile(tool.inputSchema)]),
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: tools.map(({ run: _run, ...tool }) => tool),
  }));

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const tool = tools.find((candidate) => candidate.name === request.params.name);
    if (!tool) {
      return { content: [{ type: 'text', text: 'Unknown tool' }], isError: true };
    }

    const args = request.params.arguments ?? {};
    const validate = validators.get(tool.name);
    if (!validate || !validate(args)) {
      logger.warn('MCP tool input rejected', { tool: tool.name });
      return { content: [{ type: 'text', text: 'Invalid tool input' }], isError: true };
    }

    try {
      const result = await tool.run(args);
      return { content: [{ type: 'text', text: JSON.stringify(result) ?? 'null' }] };
    } catch {
      logger.error('MCP tool execution failed', { tool: tool.name });
      return { content: [{ type: 'text', text: 'Tool execution failed' }], isError: true };
    }
  });

  logger.info('MCP tools registered', { count: tools.length });
  return server;
}
