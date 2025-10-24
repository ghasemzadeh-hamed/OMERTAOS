import fastifyJwt from '@fastify/jwt'
import oauthPlugin, { GoogleOAuth2Options } from '@fastify/oauth2'
import { FastifyInstance } from 'fastify'
import { config } from './config.js'
import { randomUUID } from 'node:crypto'

export interface UserToken {
  sub: string
  email: string
  role: 'admin' | 'manager' | 'user'
}

export async function registerAuth (app: FastifyInstance): Promise<void> {
  app.register(fastifyJwt, {
    secret: config.jwtSecret,
    sign: {
      expiresIn: '1h'
    }
  })

  if (config.google.clientId !== '' && config.google.clientSecret !== '') {
    const googleOptions: GoogleOAuth2Options = {
      name: 'googleOAuth2',
      scope: ['profile', 'email'],
      credentials: {
        client: {
          id: config.google.clientId,
          secret: config.google.clientSecret
        }
      },
      startRedirectPath: '/auth/google',
      callbackUri: '/auth/google/callback'
    }
    app.register(oauthPlugin, googleOptions)
  }

  app.decorate('authenticate', async (request: any, reply: any) => {
    try {
      await request.jwtVerify()
    } catch (error) {
      reply.code(401).send({ message: 'Unauthorized' })
    }
  })

  app.post('/auth/login', async (request, reply) => {
    const body = request.body as { email: string, password: string }
    if (!body?.email || !body?.password) {
      return reply.code(400).send({ message: 'Missing credentials' })
    }
    // In production, validate against hashed password. Here we accept any non-empty string.
    const role: UserToken['role'] = body.email.endsWith('@aion.local') ? 'admin' : 'user'
    const token = app.jwt.sign({ sub: body.email, email: body.email, role })
    return reply.send({ token })
  })

  app.get('/auth/google/callback', async function (request, reply) {
    if (!app.googleOAuth2) {
      return reply.code(503).send({ message: 'Google auth not configured' })
    }
    const token = await app.googleOAuth2.getAccessTokenFromAuthorizationCodeFlow(request)
    const profile = token?.token?.extraParams?.id_token
    const userId = randomUUID()
    const signed = app.jwt.sign({ sub: userId, email: profile?.email ?? 'google@user', role: 'user' })
    reply.redirect(`/auth/success?token=${signed}`)
  })
}

declare module 'fastify' {
  interface FastifyInstance {
    authenticate: (request: any, reply: any) => Promise<void>
    googleOAuth2?: any
  }
}
