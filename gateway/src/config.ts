import 'dotenv/config';

export interface GatewayConfig {
  port: number;
  controlPlaneUrl: string;
  jwtSecret: string;
  redisUrl: string;
  internalToken: string;
}

export const loadConfig = (): GatewayConfig => {
  const {
    GATEWAY_PORT = '8080',
    CONTROL_PLANE_URL = 'http://control:8000',
    GATEWAY_JWT_SECRET = 'supersecret',
    REDIS_URL = 'redis://redis:6379',
    INTERNAL_BRIDGE_TOKEN = 'bridge-secret'
  } = process.env;

  return {
    port: Number(GATEWAY_PORT),
    controlPlaneUrl: CONTROL_PLANE_URL,
    jwtSecret: GATEWAY_JWT_SECRET,
    redisUrl: REDIS_URL,
    internalToken: INTERNAL_BRIDGE_TOKEN
  };
};
