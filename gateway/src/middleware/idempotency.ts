import { FastifyReply, FastifyRequest } from 'fastify';
import { cacheIdempotency, getIdempotency } from '../redis.js';
import { gatewayConfig } from '../config.js';
import type { TaskResult } from '../types.js';
import { tenantFromHeader } from '../auth/claims.js';
import { createHttpError } from '../httpErrors.js';

export const idempotencyMiddleware = async (
  request: FastifyRequest,
  reply: FastifyReply
): Promise<TaskResult | void> => {
  const key = request.headers['idempotency-key'];
  if (typeof key !== 'string' || !key.trim()) {
    return;
  }

  const tenantId = tenantFromHeader(request);
  try {
    const cached = await getIdempotency(key, tenantId);
    if (cached) {
      reply.header('x-idempotent-replay', 'true');
      return JSON.parse(cached) as TaskResult;
    }
    request.headers['x-idempotency-hit'] = 'miss';
  } catch (error) {
    request.log.error({ err: error }, 'Idempotency lookup failed');
    throw createHttpError(503, 'Idempotency service unavailable', 'IDEMPOTENCY_UNAVAILABLE');
  }
};

export const persistIdempotency = async (key: string, payload: TaskResult, tenantId?: string) => {
  await cacheIdempotency(key, JSON.stringify(payload), gatewayConfig.idempotencyTtlSeconds, tenantId);
};
