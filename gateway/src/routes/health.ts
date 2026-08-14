import { FastifyInstance } from 'fastify';
import { gatewayConfig } from '../config.js';
import { redis } from '../redis.js';

const pingWithTimeout = async (url: string, timeoutMs = 2000) => {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs).unref();
  try {
    const response = await fetch(url, { signal: controller.signal, cache: 'no-store' });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeout);
  }
};

const redisHealth = async () => {
  try {
    await redis.ping();
    return 'ok';
  } catch {
    return 'degraded';
  }
};

const controlHealth = async () => {
  if (!gatewayConfig.controlBaseUrl) {
    return 'unknown';
  }

  const healthy = await pingWithTimeout(`${gatewayConfig.controlBaseUrl.replace(/\/$/, '')}/healthz`);
  return healthy ? 'ok' : 'degraded';
};

const healthHandler = async () => {
  const [redisStatus, controlStatus] = await Promise.all([redisHealth(), controlHealth()]);

  return {
    status: 'ok',
    service: 'gateway',
    dependencies: {
      redis: redisStatus,
      control: controlStatus,
    },
  };
};

export const registerHealthRoutes = (app: FastifyInstance) => {
  app.get('/healthz', healthHandler);
  app.get('/health', healthHandler);
  app.get('/healthz/auth', async (request, reply) => {
    const tokenHeader = (request.headers['x-aion-admin-token'] || request.headers['x-admin-token']) as
      | string
      | undefined;
    if (!tokenHeader || tokenHeader !== gatewayConfig.adminToken) {
      return reply.status(401).send({ status: 'unauthorized' });
    }

    return healthHandler();
  });
};
