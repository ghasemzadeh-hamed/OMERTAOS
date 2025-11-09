import { describe, expect, it, vi, beforeEach } from 'vitest';
import { rateLimitMiddleware } from '../../gateway/src/middleware/rateLimit.js';
import * as redisModule from '../../gateway/src/redis.js';

const buildReply = () => ({
  header: vi.fn(),
});

describe('rate limit middleware', () => {
  beforeEach(() => {
    vi.spyOn(redisModule, 'withRateLimitCounter').mockResolvedValue({ requests: 1, remaining: 10 });
  });

  it('allows traffic within limits', async () => {
    const request: any = { headers: { 'x-api-key': 'key' }, ip: '127.0.0.1', log: { error: vi.fn() } };
    const reply: any = buildReply();
    await rateLimitMiddleware(request, reply);
    expect(reply.header).toHaveBeenCalled();
  });

  it('throttles when exceeding limit', async () => {
    vi.spyOn(redisModule, 'withRateLimitCounter').mockResolvedValueOnce({ requests: 100, remaining: 0 });
    const request: any = { headers: { 'x-api-key': 'key' }, ip: '127.0.0.1', log: { error: vi.fn() } };
    const reply: any = buildReply();
    await expect(rateLimitMiddleware(request, reply)).rejects.toMatchObject({ statusCode: 429 });
    expect(reply.header).toHaveBeenCalledWith('retry-after', expect.any(String));
  });

  it('marks headers when redis unavailable', async () => {
    vi.spyOn(redisModule, 'withRateLimitCounter').mockRejectedValueOnce(new Error('redis down'));
    const request: any = { headers: { 'x-api-key': 'key' }, ip: '127.0.0.1', log: { error: vi.fn() } };
    const reply: any = buildReply();
    await rateLimitMiddleware(request, reply);
    expect(reply.header).toHaveBeenCalledWith('x-rate-limit-limit', 'unavailable');
    expect(reply.header).toHaveBeenCalledWith('x-rate-limit-remaining', 'unavailable');
    expect(reply.header).toHaveBeenCalledWith('x-rate-limit-reset', 'unavailable');
  });
});
