import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL ?? 'redis://localhost:6379');

export async function rateLimit(identifier: string, windowSeconds = 60, max = 120) {
  const key = `ratelimit:${identifier}`;
  const tx = redis.multi();
  tx.incr(key);
  tx.expire(key, windowSeconds, 'NX');
  const [count] = (await tx.exec()) ?? [];
  const usage = Number(Array.isArray(count) ? count[1] : count);
  return {
    success: usage <= max,
    usage
  };
}
