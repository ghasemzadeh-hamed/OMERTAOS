import { MCPServer } from '@microsoft/ai-mcp-sdk';
import { Logger } from '../logger.js';
import { OmertaClient } from '../omertaClient.js';
import { platformTools } from '../tools/platformTools.js';
import { businessTools } from '../tools/businessTools.js';
import { adminTools } from '../tools/adminTools.js';

export function buildServer(client: OmertaClient, logger: Logger) {
  const server = new MCPServer({ name: 'omertaos-wsl-bridge', version: '0.1.0' });
  const tools = [...platformTools(client), ...businessTools(client), ...adminTools(client)];
  tools.forEach((tool) => server.addTool(tool));
  logger.info('MCP tools registered', { count: tools.length });
  return server;
}
