import Fastify from 'fastify'
import { config } from './config.js'
import { TaskPayload } from './types.js'
import fetch from 'node-fetch'
import { randomUUID } from 'node:crypto'
import FastifyRateLimit from '@fastify/rate-limit'
import FastifyCors from '@fastify/cors'
import FastifyWebsocket from '@fastify/websocket'
import FastifyRedis from '@fastify/redis'
import fastifySsePlugin from 'fastify-sse-v2'

interface SSEClient {
  id: string
  send: (data: any) => void
}

export async function buildServer () {
  const app = Fastify({
    logger: true
  })

  await app.register(FastifyCors, { origin: true })
  await app.register(FastifyRateLimit, {
    max: 100,
    timeWindow: '1 minute'
  })
  await app.register(FastifyWebsocket)
  if (process.env.NODE_ENV === 'test') {
    app.decorate('redis', {
      publish: async () => 1,
      subscribe: async (_channel: string, cb: any) => {
        cb(null, 1)
        return {
          on: () => {},
          unsubscribe: async () => {}
        }
      }
    })
  } else {
    await app.register(FastifyRedis, { url: config.redisUrl, lazyConnect: true })
  }
  await app.register(fastifySsePlugin)

  const clients = new Map<string, SSEClient>()

  app.get('/health', async () => ({ status: 'ok' }))

  app.get('/stream/tasks', { websocket: true }, (connection) => {
    const id = randomUUID()
    clients.set(id, {
      id,
      send: (data: any) => connection.socket.send(JSON.stringify(data))
    })

    connection.socket.on('close', () => {
      clients.delete(id)
    })
  })

  app.get('/events/tasks', async (request, reply) => {
    const token = (request.headers.authorization as string | undefined)?.replace('Bearer ', '') ?? (request.query as any)?.token
    if (!token) {
      reply.code(401).send({ message: 'Unauthorized' })
      return
    }
    try {
      await app.jwt.verify(token)
    } catch {
      reply.code(401).send({ message: 'Unauthorized' })
      return
    }
    reply.sse({ event: 'connected', data: 'ready' })
    const listener = (message: string) => {
      reply.sse({ event: 'task_update', data: message })
    }
    const subscriber = await app.redis.subscribe('tasks:updates', (err, count) => {
      if (err) app.log.error(err, 'Redis subscribe error: %s', err?.message)
      else app.log.info({ count }, 'Subscribed to task updates')
    })
    subscriber.on('message', (_channel: string, message: string) => {
      listener(message)
    })
    request.raw.on('close', async () => {
      await subscriber.unsubscribe('tasks:updates')
      reply.raw.end()
    })
  })

  app.addHook('preHandler', async (request, reply) => {
    if (request.routerPath?.startsWith('/tasks')) {
      await app.authenticate(request, reply)
    }
  })

  app.get('/tasks', async () => {
    const res = await fetch(`${config.controlUrl}/tasks`)
    if (!res.ok) throw new Error('Control plane error')
    return await res.json()
  })

  app.post('/tasks', async (request, reply) => {
    const payload = request.body as TaskPayload
    const res = await fetch(`${config.controlUrl}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      return reply.code(res.status).send(await res.json())
    }
    const data = await res.json()
    broadcast({ type: 'task_created', task: data })
    return reply.code(202).send(data)
  })

  app.get('/tasks/:id', async (request, reply) => {
    const { id } = request.params as { id: string }
    const res = await fetch(`${config.controlUrl}/tasks/${id}`)
    if (!res.ok) {
      return reply.code(res.status).send(await res.json())
    }
    return await res.json()
  })

  app.post('/tasks/:id/cancel', async (request, reply) => {
    const { id } = request.params as { id: string }
    const res = await fetch(`${config.controlUrl}/tasks/${id}/cancel`, { method: 'POST' })
    if (!res.ok) return reply.code(res.status).send(await res.json())
    const data = await res.json()
    broadcast({ type: 'task_cancelled', task: data })
    return reply.send(data)
  })

  function broadcast (message: any) {
    const json = JSON.stringify(message)
    for (const client of clients.values()) {
      client.send(json)
    }
    app.redis.publish('tasks:updates', json).catch(err => app.log.error(err))
  }

  return app
}
