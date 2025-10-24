import { FastifyReply, FastifyRequest } from 'fastify';
import { gatewayConfig } from '../config.js';
import { withRateLimitCounter } from '../redis.js';
import { buildDefaultContext } from '../auth/index.js';

const parseWindowMs = (window: string) => {
  const [value, unit] = window.split(' ');
  const numeric = Number(value || '1');
  switch ((unit || 'minute').toLowerCase()) {
    case 's':
    case 'sec':
    case 'second':
    case 'seconds':
      return numeric * 1000;
    case 'm':
    case 'min':
    case 'minute':
    case 'minutes':
      return numeric * 60 * 1000;
    case 'h':
    case 'hr':
    case 'hour':
    case 'hours':
      return numeric * 60 * 60 * 1000;
    default:
      return 60 * 1000;
  }
};

const windowMs = parseWindowMs(gatewayConfig.rateLimit.timeWindow);

export const rateLimitMiddleware = async (request: FastifyRequest, reply: FastifyReply) => {
  if (!request.context) {
    request.context = buildDefaultContext(request);
  }
  const apiKey = request.headers['x-api-key'];
  const tenant = request.context.user?.tenant || (request.headers['x-tenant'] as string | undefined);
  const perKeyLimit = gatewayConfig.rateLimit.max;
  const perIpLimit = gatewayConfig.rateLimit.perIp;
  const perUserLimit = gatewayConfig.rateLimit.perUser;
  const userIdentifier = request.context.user?.id;
  const keyIdentifier = typeof apiKey === 'string' ? apiKey : request.ip;

  try {
    const counters = await Promise.all([
      withRateLimitCounter(keyIdentifier, windowMs, perKeyLimit, tenant, 'rl:key'),
      withRateLimitCounter(request.ip, windowMs, perIpLimit, tenant, 'rl:ip'),
      withRateLimitCounter(userIdentifier ?? keyIdentifier, windowMs, perUserLimit, tenant, 'rl:user'),
    ]);

    const [perKey, perIp, perUser] = counters;

    const resetSeconds = String(Math.ceil(Date.now() / 1000) + windowMs / 1000);
    reply.header('x-rate-limit-limit', String(perKeyLimit));
    reply.header('x-rate-limit-remaining', String(Math.max(perKeyLimit - perKey.requests, 0)));
    reply.header('x-rate-limit-reset', resetSeconds);

    if (perKey.requests > perKeyLimit || perIp.requests > perIpLimit || perUser.requests > perUserLimit) {
      reply.header('retry-after', String(Math.ceil(windowMs / 1000)));
      throw reply.tooManyRequests('Rate limit exceeded');
    }
  } catch (error) {
    request.log.error({ err: error }, 'Rate limit check failed');
    reply.header('retry-after', String(Math.ceil(windowMs / 1000)));
    throw reply.serviceUnavailable('Rate limiting unavailable');
  }
};
