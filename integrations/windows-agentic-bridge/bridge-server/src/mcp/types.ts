import type { Tool } from '@modelcontextprotocol/sdk/types.js';

export type BridgeTool = Tool & {
  run(args: Record<string, unknown>): Promise<unknown>;
};
