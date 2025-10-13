import cluster from 'cluster';
import os from 'os';
import process from 'process';
import express from 'express';
import morgan from 'morgan';
import http from 'http';
import { WebSocketServer } from 'ws';
import { pipeline, Readable } from 'stream';

const PORT = Number(process.env.PORT ?? 3000);
const CORE_URL = process.env.CORE_URL ?? 'http://localhost:8000';
const WORKER_COUNT = Number(process.env.GATEWAY_WORKERS ?? os.cpus().length);

const isPrimary = cluster.isPrimary ?? cluster.isMaster;

if (isPrimary) {
  console.log(`[gateway] primary pid=${process.pid} starting ${WORKER_COUNT} workers`);
  for (let i = 0; i < WORKER_COUNT; i += 1) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.warn(`[gateway] worker ${worker.process.pid} exited code=${code} signal=${signal}. Restarting.`);
    cluster.fork();
  });
} else {
  startWorker();
}

function startWorker() {
  const app = express();
  app.use(express.json({ limit: '1mb' }));
  app.use(morgan('combined'));

  app.get('/healthz', (_req, res) => {
    res.json({ status: 'ok', pid: process.pid });
  });

  app.post('/api/v1/requests', async (req, res) => {
    try {
      const controller = new AbortController();
      req.on('close', () => controller.abort());

      const upstreamResponse = await fetch(`${CORE_URL}/dispatch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req.body ?? {}),
        signal: controller.signal,
      });

      if (!upstreamResponse.body) {
        const text = await upstreamResponse.text();
        res.status(upstreamResponse.status).send(text);
        return;
      }

      const contentType = upstreamResponse.headers.get('content-type');
      if (contentType?.includes('text/event-stream')) {
        res.setHeader('Content-Type', contentType);
      }

      const nodeStream = Readable.fromWeb(upstreamResponse.body);
      pipeline(nodeStream, res, (error) => {
        if (error) {
          console.error('[gateway] streaming error', error);
        }
      });
    } catch (error) {
      console.error('[gateway] request forwarding failed', error);
      res.status(502).json({ error: 'gateway_error', message: 'Failed to reach control plane' });
    }
  });

  const server = http.createServer(app);
  const wsServer = new WebSocketServer({ server, path: '/ws' });

  wsServer.on('connection', (socket) => {
    socket.on('message', async (raw) => {
      let payload;
      try {
        payload = JSON.parse(raw.toString());
      } catch (error) {
        socket.send(JSON.stringify({ type: 'error', message: 'Invalid JSON payload' }));
        return;
      }

      try {
        const upstreamResponse = await fetch(`${CORE_URL}/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Accept: 'text/event-stream',
          },
          body: JSON.stringify(payload),
        });

        if (!upstreamResponse.body) {
          socket.send(JSON.stringify({ type: 'error', message: 'Empty stream from control plane' }));
          return;
        }

        const nodeStream = Readable.fromWeb(upstreamResponse.body);
        nodeStream.on('data', (chunk) => {
          socket.send(chunk.toString());
        });
        nodeStream.on('end', () => {
          socket.send(JSON.stringify({ type: 'complete' }));
        });
        nodeStream.on('error', (error) => {
          console.error('[gateway] websocket stream error', error);
          socket.send(JSON.stringify({ type: 'error', message: 'Streaming error' }));
        });
      } catch (error) {
        console.error('[gateway] websocket forwarding failed', error);
        socket.send(JSON.stringify({ type: 'error', message: 'Failed to reach control plane' }));
      }
    });
  });

  server.listen(PORT, () => {
    console.log(`[gateway] worker pid=${process.pid} listening on port ${PORT}`);
  });
}
