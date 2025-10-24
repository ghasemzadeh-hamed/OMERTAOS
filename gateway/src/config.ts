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
  outboundWebhooks: Array<{
    url: string;
    secret: string;
    topics: string[];
    maxRetries: number;
    backoffSeconds: number;
  }>;
  inboundWebhookSecret?: string;
  rateLimit: {
    max: number;
    timeWindow: string;
    perIp: number;
    perUser: number;
  };
  idempotencyTtlSeconds: number;
  environment: 'development' | 'test' | 'production';
  tls: {
    enabled: boolean;
    certPath?: string;
    keyPath?: string;
    caPaths?: string[];
    requireMtls: boolean;
    mtlsCaPath?: string;
  };
  tenancyMode: 'single' | 'multi';
  requireTenantHeader: boolean;
  consoleUsers: Record<string, { password: string; roles: string[]; tenant?: string }>;
  consoleGatewayApiKey?: string;
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

const parseConsoleUsers = (): Record<string, { password: string; roles: string[]; tenant?: string }> => {
  const raw = process.env.AION_CONSOLE_USERS;
  if (!raw) {
    return {};
  }
  const entries = raw
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean);
  const users: Record<string, { password: string; roles: string[]; tenant?: string }> = {};
  for (const entry of entries) {
    const [email, password, rolesPart, tenant] = entry.split(':');
    if (!email || !password || !rolesPart) {
      continue;
    }
    users[email.toLowerCase()] = {
      password,
      roles: rolesPart.split('|').filter(Boolean),
      tenant: tenant || process.env.AION_CONSOLE_DEFAULT_TENANT || undefined,
    };
  }
  return users;
};

const parseOutboundWebhooks = () => {
  const raw = process.env.AION_OUTBOUND_WEBHOOKS;
  if (!raw) {
    return [];
  }
  return raw
    .split(';')
    .map((value) => value.trim())
    .filter(Boolean)
    .map((entry) => {
      const [url, secret, topics, retries, backoff] = entry.split('|');
      if (!url || !secret) {
        return null;
      }
      return {
        url,
        secret,
        topics: topics ? topics.split(',') : [],
        maxRetries: Number(retries || 3),
        backoffSeconds: Number(backoff || 5),
      };
    })
    .filter((hook): hook is {
      url: string;
      secret: string;
      topics: string[];
      maxRetries: number;
      backoffSeconds: number;
    } => Boolean(hook));
};

const boolFromEnv = (value: string | undefined, fallback = false) => {
  if (typeof value === 'string') {
    return ['1', 'true', 'yes', 'on'].includes(value.toLowerCase());
  }
  return fallback;
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
  outboundWebhooks: parseOutboundWebhooks(),
  inboundWebhookSecret: process.env.AION_INBOUND_WEBHOOK_SECRET,
  rateLimit: {
    max: Number(process.env.AION_RATE_LIMIT_MAX || 60),
    timeWindow: process.env.AION_RATE_LIMIT_WINDOW || '1 minute',
    perIp: Number(process.env.AION_RATE_LIMIT_PER_IP || 30),
    perUser: Number(process.env.AION_RATE_LIMIT_PER_USER || 90),
  },
  idempotencyTtlSeconds: Number(process.env.AION_IDEMPOTENCY_TTL || 900),
  environment: (process.env.NODE_ENV as GatewayConfig['environment']) || 'development',
  tls: {
    enabled: boolFromEnv(process.env.AION_TLS_ENABLED, false),
    certPath: process.env.AION_TLS_CERT_PATH || process.env.AION_TLS_CERT,
    keyPath: process.env.AION_TLS_KEY_PATH || process.env.AION_TLS_KEY,
    caPaths: parseCaPaths(process.env.AION_TLS_CA_CHAIN),
    requireMtls: boolFromEnv(process.env.AION_TLS_REQUIRE_MTLS) || boolFromEnv(process.env.AION_MTLS_ENABLED),
    mtlsCaPath: process.env.AION_MTLS_CA_PATH,
  },
  tenancyMode: (process.env.TENANCY_MODE === 'multi' ? 'multi' : 'single') as 'single' | 'multi',
  requireTenantHeader: boolFromEnv(process.env.AION_REQUIRE_X_TENANT),
  consoleUsers: parseConsoleUsers(),
  consoleGatewayApiKey: process.env.AION_CONSOLE_GATEWAY_API_KEY,
};
