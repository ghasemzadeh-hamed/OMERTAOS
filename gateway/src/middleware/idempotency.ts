import { FastifyReply, FastifyRequest } from 'fastify';
import { cacheIdempotency, getIdempotency } from '../redis.js';
import { gatewayConfig } from '../config.js';
import type { TaskResult } from '../types.js';

export const idempotencyMiddleware = async (
  request: FastifyRequest,
  reply: FastifyReply
): Promise<TaskResult | void> => {
  const key = request.headers['idempotency-key'];
  if (typeof key !== 'string' || !key.trim()) {
    return;
  }

  const tenantId = (request.headers['x-tenant'] as string | undefined) ?? undefined;
  try {
    const cached = await getIdempotency(key, tenantId);
    if (cached) {
      reply.header('x-idempotent-replay', 'true');
      return JSON.parse(cached) as TaskResult;
    }
    request.headers['x-idempotency-hit'] = 'miss';
  } catch (error) {
    request.log.error({ err: error }, 'Idempotency lookup failed');
    reply.header('retry-after', String(Math.ceil(gatewayConfig.idempotencyTtlSeconds / 10)));
    throw reply.serviceUnavailable('Idempotency service unavailable');
  }
};

export const persistIdempotency = async (key: string, payload: TaskResult, tenantId?: string) => {
  await cacheIdempotency(key, JSON.stringify(payload), gatewayConfig.idempotencyTtlSeconds, tenantId);
};
