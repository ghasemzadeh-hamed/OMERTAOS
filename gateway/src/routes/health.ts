import { FastifyInstance } from 'fastify';

const healthHandler = async () => ({ ok: true });

export const registerHealthRoutes = (app: FastifyInstance) => {
  app.get('/healthz', healthHandler);
  app.get('/health', healthHandler);
};
