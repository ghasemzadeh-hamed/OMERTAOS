import { config } from 'dotenv';
config();

export interface GatewayConfig {
  port: number;
  host: string;
  controlGrpcEndpoint: string;
  redisUrl: string;
  apiKeys: Record<string, { roles: string[]; tenant?: string }>;
  jwtPublicKey: string | undefined;
  corsOrigins: string[];
  rateLimit: {
    max: number;
    timeWindow: string;
    perIp: number;
  };
  idempotencyTtlSeconds: number;
  environment: 'development' | 'test' | 'production';
  tls: {
    certPath?: string;
    keyPath?: string;
    caPaths?: string[];
    requireMtls: boolean;
  };
}

const parseApiKeys = (): Record<string, { roles: string[]; tenant?: string }> => {
  const raw = process.env.AION_GATEWAY_API_KEYS;
  if (!raw) {
    return {};
  }
  const entries = raw.split(',').map((pair) => pair.trim()).filter(Boolean);
  const mapped: Record<string, { roles: string[]; tenant?: string }> = {};
  for (const entry of entries) {
    const [key, rolePart, tenant] = entry.split(':');
    if (key && rolePart) {
      mapped[key] = { roles: rolePart.split('|'), tenant: tenant || undefined };
    }
  }
  return mapped;
};

const parseCaPaths = (raw?: string): string[] | undefined => {
  if (!raw) {
    return undefined;
  }
  const paths = raw
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  return paths.length ? paths : undefined;
};

export const gatewayConfig: GatewayConfig = {
  port: Number(process.env.AION_GATEWAY_PORT || 8080),
  host: process.env.AION_GATEWAY_HOST || '0.0.0.0',
  controlGrpcEndpoint: process.env.AION_CONTROL_GRPC || 'control:50051',
  redisUrl: process.env.AION_REDIS_URL || 'redis://redis:6379',
  apiKeys: parseApiKeys(),
  jwtPublicKey: process.env.AION_JWT_PUBLIC_KEY,
  corsOrigins: (process.env.AION_CORS_ORIGINS || '*')
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean),
  rateLimit: {
    max: Number(process.env.AION_RATE_LIMIT_MAX || 60),
    timeWindow: process.env.AION_RATE_LIMIT_WINDOW || '1 minute',
    perIp: Number(process.env.AION_RATE_LIMIT_PER_IP || 30),
  },
  idempotencyTtlSeconds: Number(process.env.AION_IDEMPOTENCY_TTL || 900),
  environment: (process.env.NODE_ENV as GatewayConfig['environment']) || 'development',
  tls: {
    certPath: process.env.AION_TLS_CERT,
    keyPath: process.env.AION_TLS_KEY,
    caPaths: parseCaPaths(process.env.AION_TLS_CA_CHAIN),
    requireMtls: process.env.AION_TLS_REQUIRE_MTLS === 'true',
  },
};
