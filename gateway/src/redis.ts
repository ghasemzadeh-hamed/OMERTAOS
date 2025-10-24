import Redis from 'ioredis';
import { gatewayConfig } from './config.js';

export const redis = new Redis(gatewayConfig.redisUrl, {
  enableAutoPipelining: true,
  maxRetriesPerRequest: 3,
  lazyConnect: gatewayConfig.environment === 'test',
  retryStrategy: (times) => {
    if (gatewayConfig.environment === 'test') {
      return null;
    }
    return Math.min(times * 50, 2000);
  },
});

if (gatewayConfig.environment === 'test') {
  redis.on('error', (error) => {
    if (process.env.VITEST) {
      // Silence connection noise during tests while still surfacing unexpected errors when requested.
      return;
    }
    console.warn('Redis connection error (test env)', error);
  });
}

const idemKey = (key: string, tenantId?: string) =>
  tenantId ? `idem:${tenantId}:${key}` : `idem:${key}`;

const rateKey = (prefix: string, identifier: string, tenantId?: string) =>
  tenantId ? `${prefix}:${tenantId}:${identifier}` : `${prefix}:${identifier}`;

export const cacheIdempotency = async (key: string, payload: string, ttlSeconds: number, tenantId?: string) => {
  await redis.set(idemKey(key, tenantId), payload, 'EX', ttlSeconds);
};

export const getIdempotency = async (key: string, tenantId?: string): Promise<string | null> => {
  return redis.get(idemKey(key, tenantId));
};

export const withRateLimitCounter = async (
  identifier: string,
  windowMs: number,
  limit: number,
  tenantId?: string,
  prefix = 'rl'
) => {
  const bucket = rateKey(prefix, identifier, tenantId);
  const windowKey = `${bucket}:${Math.floor(Date.now() / windowMs)}`;
  const ttl = Math.ceil(windowMs / 1000);
  const [[, count], [, _]] = await redis.multi().incr(windowKey).expire(windowKey, ttl).exec();
  const requests = Number(count);
  const remaining = Math.max(limit - requests, 0);
  return { requests, remaining };
};

export const closeRedis = async () => {
  await redis.quit();
};
