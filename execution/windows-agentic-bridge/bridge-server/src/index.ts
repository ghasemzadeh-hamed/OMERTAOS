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
  await server.serve();
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});
