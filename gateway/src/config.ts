import 'dotenv/config'

export const config = {
  port: Number(process.env.GATEWAY_PORT ?? 8080),
  jwtSecret: process.env.JWT_SECRET ?? 'changeme',
  controlUrl: process.env.CONTROL_URL ?? 'http://localhost:8000',
  redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379/0',
  google: {
    clientId: process.env.GOOGLE_CLIENT_ID ?? '',
    clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? ''
  }
}
