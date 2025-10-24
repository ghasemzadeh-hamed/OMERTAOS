import { buildServer } from './routes.js'
import { registerAuth } from './auth.js'
import { config } from './config.js'

async function start () {
  const app = await buildServer()
  await registerAuth(app)

  await app.listen({ port: config.port, host: '0.0.0.0' })
  app.log.info(`Gateway started on port ${config.port}`)
}

start().catch(err => {
  console.error(err)
  process.exit(1)
})
