import Fastify from 'fastify';
import compress from '@fastify/compress';
import helmet from '@fastify/helmet';
import websocket from '@fastify/websocket';
import { authPreHandler } from './auth.js';
import { gatewayConfig } from './config.js';
import { cacheIdempotency, getIdempotency, redis } from './redis.js';
import { createControlClient } from './grpcClient.js';
import { TaskRequest, TaskResult } from './types.js';
import { randomUUID } from 'crypto';
import { FastifyRequest } from 'fastify';
import { EventEmitter } from 'node:events';
import { Metadata } from '@grpc/grpc-js';
import cors from '@fastify/cors';
import fastifySsePlugin from 'fastify-sse-v2';

const app = Fastify({
  logger: true,
  trustProxy: true,
  genReqId: () => randomUUID(),
});

app.register(helmet, { global: true });
app.register(compress);
app.register(websocket);
app.register(fastifySsePlugin);
app.register(cors, { origin: gatewayConfig.corsOrigins, credentials: true });

const controlClient = createControlClient();
const streamEmitter = new EventEmitter();

const windowMs = (() => {
  const window = gatewayConfig.rateLimit.timeWindow;
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
})();

const rateLimitCheck = async (request: FastifyRequest) => {
  const identifier = request.headers['x-api-key'] || request.ip;
  const bucket = `rl:${identifier}`;
  const now = Date.now();
  const windowKey = `${bucket}:${Math.floor(now / windowMs)}`;
  const ttl = Math.ceil(windowMs / 1000);
  const [[, count], [, _]] = await redis
    .multi()
    .incr(windowKey)
    .expire(windowKey, ttl)
    .exec();
  const requests = Number(count);
  if (requests > gatewayConfig.rateLimit.max) {
    throw app.httpErrors.tooManyRequests('Rate limit exceeded');
  }
};

const invokeControlUnary = (method: 'Submit' | 'StatusById', payload: any) => {
  return new Promise<any>((resolve, reject) => {
    const metadata = new Metadata();
    metadata.add('x-request-id', payload.requestId || randomUUID());
    controlClient[method](payload, metadata, (err: Error | null, response: any) => {
      if (err) {
        reject(err);
      } else {
        resolve(response);
      }
    });
  });
};

const pollStatus = async (taskId: string): Promise<TaskResult | null> => {
  try {
    const response = await invokeControlUnary('StatusById', { taskId });
    if (!response) {
      return null;
    }
    return {
      schemaVersion: response.schemaVersion,
      taskId: response.taskId,
      intent: response.intent,
      status: response.status,
      engine: response.engine,
      result: response.result,
      usage: response.usage,
      error: response.error,
    } as TaskResult;
  } catch (error) {
    app.log.error({ err: error }, 'Failed to fetch status');
    return null;
  }
};

const streamTask = async (taskId: string) => {
  const result = await pollStatus(taskId);
  if (result) {
    streamEmitter.emit(taskId, result);
  }
};

app.addHook('onRequest', async (request) => {
  await rateLimitCheck(request);
});

app.addHook('preHandler', authPreHandler(['user', 'manager', 'admin']));

app.post<{ Body: TaskRequest }>('/v1/tasks', async (request, reply) => {
  const idempotencyKey = request.headers['idempotency-key'];
  if (typeof idempotencyKey === 'string') {
    const cached = await getIdempotency(idempotencyKey);
    if (cached) {
      reply.header('x-idempotent-replay', 'true');
      return JSON.parse(cached) as TaskResult;
    }
  }

  const taskId = randomUUID();
  const payload = {
    schemaVersion: request.body.schemaVersion || '1.0',
    intent: request.body.intent,
    params: Object.fromEntries(Object.entries(request.body.params || {}).map(([k, v]) => [k, String(v)])),
    preferredEngine: request.body.preferredEngine || 'auto',
    priority: request.body.priority || 'normal',
    sla: request.body.sla,
    metadata: request.body.metadata,
    requestId: request.id,
    taskId,
  };

  const response = await invokeControlUnary('Submit', payload);
  const result: TaskResult = {
    schemaVersion: response.schemaVersion,
    taskId: response.taskId,
    intent: response.intent,
    status: response.status,
    engine: response.engine,
    result: response.result,
    usage: response.usage,
    error: response.error,
  };

  if (typeof idempotencyKey === 'string') {
    await cacheIdempotency(idempotencyKey, JSON.stringify(result), 15 * 60);
  }

  reply.header('x-request-id', request.id);
  setImmediate(() => streamTask(result.taskId));
  return result;
});

app.get('/v1/tasks/:id', async (request, reply) => {
  const { id } = request.params as { id: string };
  const result = await pollStatus(id);
  if (!result) {
    throw app.httpErrors.notFound('Task not found');
  }
  reply.header('x-request-id', request.id);
  return result;
});

app.get('/v1/stream/:id', { websocket: false }, async (request, reply) => {
  const { id } = request.params as { id: string };
  reply.raw.setHeader('Content-Type', 'text/event-stream');
  reply.raw.setHeader('Cache-Control', 'no-cache');
  reply.raw.setHeader('Connection', 'keep-alive');
  reply.sse({ data: JSON.stringify({ type: 'heartbeat' }) });

  const listener = (payload: TaskResult) => {
    reply.sse({ data: JSON.stringify({ type: 'result', payload }) });
  };

  streamEmitter.on(id, listener);
  const interval = setInterval(async () => {
    const status = await pollStatus(id);
    if (status) {
      reply.sse({ data: JSON.stringify({ type: 'status', payload: status }) });
      if (status.status !== 'PENDING' && status.status !== 'RUNNING') {
        clearInterval(interval);
      }
    }
  }, 2000);

  request.raw.on('close', () => {
    clearInterval(interval);
    streamEmitter.removeListener(id, listener);
  });
});

app.get('/v1/ws', { websocket: true }, (connection, request) => {
  connection.socket.send(
    JSON.stringify({ type: 'info', message: 'send {"op":"subscribe","taskId":"..."}' })
  );
  const subscribe = (taskId: string) => {
    const listener = (payload: TaskResult) => {
      connection.socket.send(JSON.stringify({ type: 'result', payload }));
    };
    streamEmitter.on(taskId, listener);
    const interval = setInterval(async () => {
      const status = await pollStatus(taskId);
      if (status) {
        connection.socket.send(JSON.stringify({ type: 'status', payload: status }));
        if (status.status !== 'PENDING' && status.status !== 'RUNNING') {
          clearInterval(interval);
        }
      }
    }, 2000);
    connection.socket.once('close', () => {
      streamEmitter.removeListener(taskId, listener);
      clearInterval(interval);
    });
  };

  connection.socket.on('message', (message) => {
    try {
      const parsed = JSON.parse(message.toString());
      if (parsed.op === 'subscribe' && typeof parsed.taskId === 'string') {
        subscribe(parsed.taskId);
      }
    } catch (error) {
      connection.socket.send(JSON.stringify({ type: 'error', message: 'invalid message' }));
    }
  });
});

app.get('/healthz', async () => {
  try {
    const redisPing = await redis.ping();
    return { status: 'ok', redis: redisPing };
  } catch (error) {
    app.log.warn({ err: error }, 'Redis health check failed');
    return { status: 'degraded', redis: 'unreachable' };
  }
});

const start = async () => {
  try {
    await app.listen({ host: gatewayConfig.host, port: gatewayConfig.port });
    app.log.info(`Gateway listening on ${gatewayConfig.host}:${gatewayConfig.port}`);
  } catch (err) {
    app.log.error({ err }, 'Failed to start gateway');
    process.exit(1);
  }
};

if (process.env.NODE_ENV !== 'test') {
  start();
}

export default app;
