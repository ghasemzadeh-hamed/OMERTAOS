import { describe, expect, it, vi, beforeEach } from 'vitest';
import { idempotencyMiddleware, persistIdempotency } from '../../gateway/src/middleware/idempotency.js';
import * as redisModule from '../../gateway/src/redis.js';

const buildReply = () => ({
  header: vi.fn(),
});

describe('idempotency middleware', () => {
  beforeEach(() => {
    vi.spyOn(redisModule, 'getIdempotency').mockResolvedValue(null);
    vi.spyOn(redisModule, 'cacheIdempotency').mockResolvedValue();
  });

  it('returns cached payload when available', async () => {
    vi.spyOn(redisModule, 'getIdempotency').mockResolvedValue('{"taskId":"1"}');
    const request: any = { headers: { 'idempotency-key': 'abc', 'tenant-id': 'tenant-1' }, log: { error: vi.fn() } };
    const reply: any = buildReply();
    const cached = await idempotencyMiddleware(request, reply);
    expect(cached).toEqual({ taskId: '1' });
    expect(reply.header).toHaveBeenCalledWith('x-idempotent-replay', 'true');
  });

  it('stores results with tenant namespace', async () => {
    const payload = { taskId: '2' } as any;
    await persistIdempotency('abc', payload, 'tenant-1');
    expect(redisModule.cacheIdempotency).toHaveBeenCalledWith('abc', JSON.stringify(payload), expect.any(Number), 'tenant-1');
  });

  it('fails closed when redis errors', async () => {
    vi.spyOn(redisModule, 'getIdempotency').mockRejectedValue(new Error('boom'));
    const request: any = { headers: { 'idempotency-key': 'abc' }, log: { error: vi.fn() } };
    const reply: any = buildReply();
    await expect(idempotencyMiddleware(request, reply)).rejects.toMatchObject({ statusCode: 503 });
  });
});
