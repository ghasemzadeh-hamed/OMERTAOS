import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { buildServer } from '../src/routes.js'
import { registerAuth } from '../src/auth.js'

let app: Awaited<ReturnType<typeof buildServer>>

describe('gateway routes', () => {
  beforeAll(async () => {
    app = await buildServer()
    await registerAuth(app)
  })

  afterAll(async () => {
    await app.close()
  })

  it('returns health status', async () => {
    const res = await app.inject({ method: 'GET', url: '/health' })
    expect(res.statusCode).toBe(200)
    expect(res.json()).toEqual({ status: 'ok' })
  })
})
