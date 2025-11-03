import { FastifyReply, FastifyRequest } from 'fastify';
import { gatewayConfig } from '../config.js';
import { withRateLimitCounter } from '../redis.js';
import { tenantFromHeader } from '../auth/claims.js';

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
  if (gatewayConfig.environment === 'test') {
    return;
  }

  const apiKey = request.headers['x-api-key'];
  const tenant = tenantFromHeader(request);
  const identifier = typeof apiKey === 'string' ? apiKey : request.ip;
  const perKeyLimit = gatewayConfig.rateLimit.max;
  const perIpLimit = gatewayConfig.rateLimit.perIp;

  try {
    const [{ requests: perKeyRequests }, { requests: perIpRequests }] = await Promise.all([
      withRateLimitCounter(identifier, windowMs, perKeyLimit, tenant, 'rl:key'),
      withRateLimitCounter(request.ip, windowMs, perIpLimit, tenant, 'rl:ip'),
    ]);

    reply.header('x-rate-limit-limit', String(perKeyLimit));
    reply.header('x-rate-limit-remaining', String(Math.max(perKeyLimit - perKeyRequests, 0)));
    reply.header('x-rate-limit-reset', String(Math.ceil(Date.now() / 1000) + windowMs / 1000));

    if (perKeyRequests > perKeyLimit || perIpRequests > perIpLimit) {
      throw reply.tooManyRequests('Rate limit exceeded');
    }
  } catch (error) {
    request.log.error({ err: error }, 'Rate limit check failed');
    reply.header('x-rate-limit-limit', 'unavailable');
    reply.header('x-rate-limit-remaining', 'unavailable');
    reply.header('x-rate-limit-reset', 'unavailable');
    return;
  }
};
