import Fastify, { FastifyRequest } from 'fastify';
import compress from '@fastify/compress';
import helmet from '@fastify/helmet';
import websocket from '@fastify/websocket';
import { authPreHandler } from './auth/index.js';
import { tenantFromHeader } from './auth/claims.js';
import { gatewayConfig } from './config.js';
import cors from '@fastify/cors';
import fastifySsePlugin from 'fastify-sse-v2';
import { randomUUID } from 'node:crypto';
import { EventEmitter } from 'node:events';
import { pathToFileURL } from 'node:url';
import { Metadata } from '@grpc/grpc-js';
import { createControlClient } from './server/grpc.js';
import { idempotencyMiddleware, persistIdempotency } from './middleware/idempotency.js';
import { rateLimitMiddleware } from './middleware/rateLimit.js';
import { ZodError } from 'zod';
import type {
  DevKernelRequest,
  DevKernelResponse,
  TaskRequest,
  TaskRequestInput,
  TaskResult,
} from './types.js';
import { devKernelRequestSchema, taskRequestSchema } from './types.js';
import { shutdownTelemetry, startTelemetry } from './telemetry.js';
import { registerConfigRoutes } from './routes/config.js';
import { registerSealRoutes } from './routes/seal.js';
import {
  buildDevKernelPayload,
  callDevKernel,
  devKernelEnabled,
  shouldUseDevKernel,
} from './server/devKernelProxy.js';
import { createHttpError } from './httpErrors.js';
import { logInteraction, resolveModelForAgent } from './services/selfEvolving.js';

const app = Fastify({
  logger: true,
  trustProxy: true,
  genReqId: () => randomUUID(),
});

app.register(helmet, { global: true });
app.register(compress);
app.register(websocket);
app.register(fastifySsePlugin);
const corsOriginSetting =
  gatewayConfig.corsOrigins.length === 1 && gatewayConfig.corsOrigins[0] === '*'
    ? true
    : gatewayConfig.corsOrigins;

app.register(cors, {
  origin: corsOriginSetting,
  credentials: gatewayConfig.corsAllowCredentials,
});

app.addHook('onRequest', async (request, reply) => {
  reply.header('x-request-id', request.id);
  const correlation = request.headers['x-correlation-id'];
  if (typeof correlation === 'string') {
    reply.header('x-correlation-id', correlation);
  } else {
    reply.header('x-correlation-id', request.id);
  }
});

const controlClient = createControlClient();
const streamEmitter = new EventEmitter();
const healthHandler = async () => ({
  status: 'ok',
  service: 'gateway',
  profile: gatewayConfig.profile,
  seal_enabled: gatewayConfig.featureSeal,
});

const invokeControlUnary = (method: 'Submit' | 'StatusById', payload: any, metadata: Metadata) => {
  return new Promise<any>((resolve, reject) => {
    controlClient[method](payload, metadata, (err: Error | null, response: any) => {
      if (err) {
        reject(err);
      } else {
        resolve(response);
      }
    });
  });
};

const resolveTenantHeader = (request: FastifyRequest): string | undefined => tenantFromHeader(request);

const normaliseString = (value: unknown): string | undefined => {
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : undefined;
  }
  return undefined;
};

const ensureMetadataRecord = (value: unknown): Record<string, unknown> => {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }
  return {};
};

const extractAgentId = (task: TaskRequest, request: FastifyRequest): string => {
  const metadata = ensureMetadataRecord(task.metadata);
  const candidates = [metadata.agent_id, metadata.agentId, metadata.agent];
  for (const candidate of candidates) {
    const normalised = normaliseString(candidate);
    if (normalised) {
      return normalised;
    }
  }
  return normaliseString(request.aionContext.user?.id) ?? 'unknown-agent';
};

const extractPreferredModel = (task: TaskRequest): string => {
  const metadata = ensureMetadataRecord(task.metadata);
  const candidates = [
    metadata.model_name,
    metadata.model,
    metadata.default_model,
    metadata.preferred_model,
  ];
  for (const candidate of candidates) {
    const normalised = normaliseString(candidate);
    if (normalised) {
      return normalised;
    }
  }
  return 'auto';
};

const summariseTaskInput = (task: TaskRequest): string => {
  try {
    return JSON.stringify({
      intent: task.intent,
      params: task.params ?? {},
      metadata: task.metadata ?? {},
    });
  } catch {
    return task.intent;
  }
};

const summariseTaskOutput = (result: TaskResult): string => {
  const payload = result.result ?? result.error ?? {};
  try {
    return JSON.stringify(payload ?? {});
  } catch {
    if (typeof payload === 'string') {
      return payload;
    }
    return JSON.stringify({ status: result.status });
  }
};

const buildMetadata = (request: FastifyRequest) => {
  const metadata = new Metadata();
  metadata.add('x-request-id', request.id);
  if (request.headers['authorization']) {
    metadata.add('authorization', String(request.headers['authorization']));
  }
  const tenantFromHeader = resolveTenantHeader(request);
  if (tenantFromHeader) {
    metadata.add('tenant-id', tenantFromHeader);
  }
  if (request.headers['traceparent']) {
    metadata.add('traceparent', String(request.headers['traceparent']));
  }
  return metadata;
};

const pollStatus = async (taskId: string, request: FastifyRequest): Promise<TaskResult | null> => {
  try {
    const response = await invokeControlUnary('StatusById', { taskId }, buildMetadata(request));
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
    request.log.error({ err: error }, 'Failed to fetch status');
    return null;
  }
};

const streamTask = async (taskId: string, request: FastifyRequest) => {
  const result = await pollStatus(taskId, request);
  if (result) {
    streamEmitter.emit(taskId, result);
  }
};

app.addHook('onRequest', async (request, reply) => {
  await rateLimitMiddleware(request, reply);
});

app.addHook('preHandler', authPreHandler(['user', 'manager', 'admin']));

app.get('/healthz', healthHandler);
app.get('/health', healthHandler);

app.post<{ Body: DevKernelRequest }>('/api/dev/kernel', async (request, reply) => {
  if (!devKernelEnabled()) {
    throw createHttpError(503, 'Dev kernel is disabled', 'DEV_KERNEL_DISABLED');
  }

  let payload: DevKernelRequest;
  try {
    payload = devKernelRequestSchema.parse(request.body);
  } catch (error) {
    if (error instanceof ZodError) {
      return reply.status(400).send({
        error: 'ValidationError',
        message: 'Invalid dev kernel request',
        issues: error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message,
          code: issue.code,
        })),
      });
    }
    throw error;
  }

  try {
    const response = await callDevKernel(payload);
    return response;
  } catch (error) {
    request.log.error({ err: error }, 'Dev kernel proxy request failed');
    throw createHttpError(503, 'Dev kernel unavailable', 'DEV_KERNEL_UNAVAILABLE');
  }
});

app.post<{ Body: TaskRequestInput }>('/v1/tasks', async (request, reply) => {
  let validatedBody: TaskRequest;
  try {
    validatedBody = taskRequestSchema.parse(request.body);
  } catch (error) {
    request.log.warn({ err: error }, 'Invalid task request payload');
    if (error instanceof ZodError) {
      return reply.status(400).send({
        error: 'ValidationError',
        message: 'Invalid task request',
        issues: error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message,
          code: issue.code,
        })),
      });
    }
    throw error;
  }

  const cached = await idempotencyMiddleware(request, reply);
  if (cached) {
    return cached;
  }

  const agentId = extractAgentId(validatedBody, request);
  const defaultModel = extractPreferredModel(validatedBody);
  const resolvedModel = await resolveModelForAgent(agentId, defaultModel, request.log);
  const metadata = ensureMetadataRecord(validatedBody.metadata);
  if (!metadata.agent_id) {
    metadata.agent_id = agentId;
  }
  metadata.resolved_model = resolvedModel;
  const routingMetadata = ensureMetadataRecord(metadata.routing);
  routingMetadata.resolved_model = resolvedModel;
  routingMetadata.decided_at = new Date().toISOString();
  metadata.routing = routingMetadata;
  validatedBody = { ...validatedBody, metadata };

  const idempotencyKey = typeof request.headers['idempotency-key'] === 'string' ? request.headers['idempotency-key'] : undefined;
  const tenantId = resolveTenantHeader(request);

  const taskId = randomUUID();
  const inputSummary = summariseTaskInput(validatedBody);
  const userId = normaliseString(request.aionContext.user?.id);
  const persistInteraction = (result: TaskResult) => {
    void logInteraction(
      {
        agentId,
        userId,
        modelVersion: resolvedModel || result.engine?.route || defaultModel,
        inputText: inputSummary,
        outputText: summariseTaskOutput(result),
        channel: gatewayConfig.selfEvolving.defaultChannel,
      },
      request.log,
    );
  };
  if (shouldUseDevKernel(request)) {
    if (!devKernelEnabled()) {
      throw createHttpError(503, 'Dev kernel is disabled', 'DEV_KERNEL_DISABLED');
    }

    let devResponse: DevKernelResponse;
    try {
      const payload = buildDevKernelPayload(validatedBody, request);
      devResponse = await callDevKernel(payload);
    } catch (error) {
      request.log.error({ err: error }, 'Dev kernel invocation failed');
      throw createHttpError(503, 'Dev kernel unavailable', 'DEV_KERNEL_UNAVAILABLE');
    }

    const status: TaskResult['status'] = devResponse.type === 'error' ? 'ERROR' : 'OK';
    const resultPayload =
      devResponse.type === 'error'
        ? undefined
        : { type: devResponse.type, content: devResponse.content };
    const errorPayload =
      devResponse.type === 'error'
        ? {
            code: 'DEV_KERNEL_ERROR',
            message:
              typeof devResponse.content === 'string'
                ? devResponse.content
                : 'Dev kernel reported an error',
          }
        : null;

    const result: TaskResult = {
      schemaVersion: validatedBody.schemaVersion,
      taskId,
      intent: validatedBody.intent,
      status,
      engine: {
        route: 'dev-kernel',
        chosen_by: 'gateway',
        reason: 'Requested via dev mode header',
      },
      result: resultPayload ? { devKernel: resultPayload } : undefined,
      error: errorPayload,
    };

    persistInteraction(result);

    if (idempotencyKey) {
      try {
        await persistIdempotency(idempotencyKey, result, tenantId);
      } catch (error) {
        request.log.error({ err: error }, 'Failed to persist idempotency result');
        throw createHttpError(503, 'Idempotency cache unavailable', 'IDEMPOTENCY_UNAVAILABLE');
      }
    }

    return result;
  }

  const payload = {
    ...validatedBody,
    taskId,
  };

  const response = await invokeControlUnary('Submit', payload, buildMetadata(request));
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

  persistInteraction(result);

  if (idempotencyKey) {
    try {
      await persistIdempotency(idempotencyKey, result, tenantId);
    } catch (error) {
      request.log.error({ err: error }, 'Failed to persist idempotency result');
      throw createHttpError(503, 'Idempotency cache unavailable', 'IDEMPOTENCY_UNAVAILABLE');
    }
  }

  return result;
});

app.get('/v1/tasks/:id', async (request, reply) => {
  const { id } = request.params as { id: string };
  const result = await pollStatus(id, request);
  if (!result) {
    throw createHttpError(404, 'Task not found', 'TASK_NOT_FOUND');
  }
  return result;
});

app.get('/v1/stream/:id', async (request, reply) => {
  const { id } = request.params as { id: string };
  reply.raw.setHeader('Content-Type', 'text/event-stream');
  reply.raw.setHeader('Cache-Control', 'no-cache');
  reply.raw.setHeader('Connection', 'keep-alive');

  const listener = (result: TaskResult) => {
    reply.sse({ id: result.taskId, data: JSON.stringify(result) });
  };

  streamEmitter.on(id, listener);
  request.raw.on('close', () => {
    streamEmitter.off(id, listener);
  });
  await streamTask(id, request);
});

app.register(async (instance) => {
  instance.get('/v1/ws', { websocket: true }, (connection, request) => {
    const { socket } = connection;
    socket.send(JSON.stringify({ type: 'welcome', requestId: request.id }));
    socket.on('message', async (message: Buffer) => {
      try {
        const parsed = JSON.parse(message.toString());
        if (parsed.action === 'subscribe' && parsed.taskId) {
          const listener = (result: TaskResult) => {
            socket.send(JSON.stringify({ type: 'task', payload: result }));
          };
          streamEmitter.on(parsed.taskId, listener);
          socket.once('close', () => streamEmitter.off(parsed.taskId, listener));
          await streamTask(parsed.taskId, request);
        }
      } catch (error) {
        socket.send(JSON.stringify({ type: 'error', message: (error as Error).message }));
      }
    });
    const heartbeat = setInterval(() => {
      if (socket.readyState === socket.OPEN) {
        socket.send(JSON.stringify({ type: 'heartbeat', ts: Date.now() }));
      }
    }, 15_000);
    socket.once('close', () => clearInterval(heartbeat));
  });
});

registerConfigRoutes(app);
registerSealRoutes(app);

app.setErrorHandler((error, request, reply) => {
  request.log.error({ err: error }, 'Unhandled gateway error');
  if (reply.raw.headersSent) {
    return reply;
  }
  return reply.status(error.statusCode || 500).send({
    error: 'GatewayError',
    message: error.message,
    statusCode: error.statusCode || 500,
  });
});

export const start = async () => {
  const telemetryEnabled = await startTelemetry(gatewayConfig.telemetry.serviceName);
  app.addHook('onClose', async () => {
    if (telemetryEnabled) {
      await shutdownTelemetry();
    }
  });
  await app.listen({ port: gatewayConfig.port, host: gatewayConfig.host });
  app.log.info(`Gateway listening on ${gatewayConfig.host}:${gatewayConfig.port}`);
  return app;
};

const shouldAutostart = (): boolean => {
  if (process.env.NODE_ENV === 'test') {
    return false;
  }
  const entryFile = process.argv[1];
  if (!entryFile) {
    return false;
  }
  try {
    return pathToFileURL(entryFile).href === import.meta.url;
  } catch {
    return false;
  }
};

if (shouldAutostart()) {
  start().catch((error) => {
    app.log.error({ err: error }, 'Gateway failed to start');
    process.exitCode = 1;
  });
}

export type GatewayServer = typeof app;

export default app;
