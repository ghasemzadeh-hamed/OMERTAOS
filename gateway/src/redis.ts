import Redis from 'ioredis';
import { gatewayConfig } from './config.js';

export const redis = new Redis(gatewayConfig.redisUrl, {
  enableAutoPipelining: true,
  maxRetriesPerRequest: 3,
});

export const cacheIdempotency = async (key: string, payload: string, ttlSeconds: number) => {
  await redis.set(`idem:${key}`, payload, 'EX', ttlSeconds);
};

export const getIdempotency = async (key: string): Promise<string | null> => {
  return redis.get(`idem:${key}`);
};

export const closeRedis = async () => {
  await redis.quit();
};
