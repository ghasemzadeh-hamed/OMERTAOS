import Fastify from 'fastify';
import websocket from '@fastify/websocket';
import cors from '@fastify/cors';
import { loadConfig } from './config.js';
import { registerAuth } from './auth.js';
import { registerTelemetry } from './telemetry.js';
import type { TaskRequest, TelemetryEvent } from './types.js';
import fetch from 'node-fetch';

const config = loadConfig();

const app = Fastify({
  logger: {
    transport: {
      target: 'pino-pretty'
    }
  }
});

await app.register(cors, { origin: true, credentials: true });
await registerAuth(app, config.jwtSecret);
await registerTelemetry(app);
await app.register(websocket);

app.decorate('config', config);

app.post('/task', {
  preHandler: app.authenticate,
  schema: {
    body: {
      type: 'object',
      required: ['task_id', 'intent', 'params'],
      properties: {
        task_id: { type: 'string' },
        intent: { type: 'string' },
        params: { type: 'object' },
        preferred_engine: { type: 'string', enum: ['local', 'api', 'hybrid'] },
        priority: { type: 'string', enum: ['low', 'medium', 'high'] }
      }
    }
  }
}, async (request) => {
  const payload = request.body as TaskRequest;
  const response = await fetch(`${config.controlPlaneUrl}/api/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: request.headers.authorization ?? '',
      'x-internal-token': config.internalToken
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const message = await response.text();
    throw app.httpErrors.badGateway(message);
  }

  const data = await response.json();
  return data;
});

app.get('/ws/stream/:taskId', { websocket: true }, (connection, request) => {
  const taskId = (request.params as { taskId: string }).taskId;
  const unsubscribe = app.telemetry.subscribe(taskId, (event) => {
    connection.socket.send(JSON.stringify(event));
  });

  connection.socket.on('close', () => unsubscribe());
});

app.post<{ Body: TelemetryEvent }>('/internal/telemetry', async (request, reply) => {
  const token = request.headers['x-internal-token'];
  if (token !== config.internalToken) {
    throw app.httpErrors.unauthorized('Invalid bridge token');
  }
  app.telemetry.publish(request.body);
  reply.status(202).send({ ok: true });
});

app.get('/health', async () => ({ status: 'ok' }));

const start = async () => {
  try {
    await app.listen({ port: config.port, host: '0.0.0.0' });
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

start();
