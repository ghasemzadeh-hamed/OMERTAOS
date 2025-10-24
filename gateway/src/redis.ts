import Redis from 'ioredis';
import { gatewayConfig } from './config.js';

export const redis = new Redis(gatewayConfig.redisUrl, {
  enableAutoPipelining: true,
  maxRetriesPerRequest: 3,
});

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
