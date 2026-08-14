import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { loadConfig } from './config.js';
import { Logger } from './logger.js';
import { OmertaClient } from './omertaClient.js';
import { buildServer } from './mcp/server.js';

async function main() {
  const config = loadConfig();
  const logger = new Logger(config.logLevel as any);
  const client = new OmertaClient(config, logger);

  const server = buildServer(client, logger);
  logger.info('Starting OMERTA MCP bridge');
  await server.connect(new StdioServerTransport());
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
