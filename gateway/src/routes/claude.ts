import { FastifyInstance } from 'fastify';

const marketplaceId = 'wshobson/agents';
const recommendedPlugins = [
  'python-development@wshobson/agents',
  'javascript-typescript@wshobson/agents',
  'backend-development@wshobson/agents',
  'kubernetes-operations@wshobson/agents',
  'cloud-infrastructure@wshobson/agents',
  'security-scanning@wshobson/agents',
  'code-review-ai@wshobson/agents',
  'full-stack-orchestration@wshobson/agents',
];

export const registerClaudeRoutes = (app: FastifyInstance) => {
  app.get('/api/claude/recommended', async () => ({
    marketplace: marketplaceId,
    recommendedPlugins,
  }));
};
