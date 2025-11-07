import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { SecretProvider, SecretProviderError } from '@aionos/secret-provider';
import { config } from 'dotenv';

const inferredEnvFiles = new Set<string>();
const explicitEnv = process.env.ENV_FILE;
if (explicitEnv) {
  inferredEnvFiles.add(path.resolve(explicitEnv));
}

inferredEnvFiles.add(path.resolve(process.cwd(), '.env'));
inferredEnvFiles.add(path.resolve(process.cwd(), '..', '.env'));

const moduleDir = path.dirname(fileURLToPath(import.meta.url));
inferredEnvFiles.add(path.resolve(moduleDir, '..', '.env'));
inferredEnvFiles.add(path.resolve(moduleDir, '..', '..', '.env'));

for (const envFile of inferredEnvFiles) {
  if (fs.existsSync(envFile)) {
    config({ path: envFile, override: false });
  }
}

export interface GatewayConfig {
  port: number;
  host: string;
  controlGrpcEndpoint: string;
  controlBaseUrl: string;
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
  telemetry: {
    enabled: boolean;
    serviceName: string;
  };
  profile: 'user' | 'professional' | 'enterprise-vip';
  featureSeal: boolean;
  adminToken: string;
  devKernel: {
    enabled: boolean;
    url: string;
    profile: string;
  };
}

const parseApiKeysString = (raw?: string): Record<string, { roles: string[]; tenant?: string }> => {
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

const parseApiKeysSecret = (secret: Record<string, unknown> | string): Record<string, { roles: string[]; tenant?: string }> => {
  if (typeof secret === 'string') {
    return parseApiKeysString(secret);
  }
  if (typeof secret.value === 'string') {
    return parseApiKeysString(secret.value);
  }
  const keys: Record<string, { roles: string[]; tenant?: string }> = {};
  const payload = secret.keys && typeof secret.keys === 'object' ? secret.keys : secret;
  for (const [apiKey, value] of Object.entries(payload)) {
    if (apiKey === 'value') {
      continue;
    }
    if (typeof value === 'string') {
      keys[apiKey] = { roles: value.split(',').map((role) => role.trim()).filter(Boolean) };
      continue;
    }
    if (value && typeof value === 'object' && 'roles' in value) {
      const rolesValue = (value as { roles: unknown }).roles;
      let roles: string[] = [];
      if (Array.isArray(rolesValue)) {
        roles = rolesValue.map((role) => String(role));
      } else if (typeof rolesValue === 'string') {
        roles = rolesValue.split(/[,|]/).map((role) => role.trim()).filter(Boolean);
      }
      const tenantValue = (value as { tenant?: unknown }).tenant;
      keys[apiKey] = {
        roles,
        tenant: typeof tenantValue === 'string' && tenantValue ? tenantValue : undefined,
      };
    }
  }
  return keys;
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

const profile = (process.env.AION_PROFILE || 'user').toLowerCase() as GatewayConfig['profile'];
const featureSeal = process.env.FEATURE_SEAL === '1' || profile === 'enterprise-vip';

let secretProvider: SecretProvider | null = null;
if (process.env.VAULT_ADDR) {
  try {
    secretProvider = new SecretProvider({});
  } catch (error) {
    if (error instanceof SecretProviderError) {
      throw error;
    }
    throw new Error(`Failed to initialise Vault secret provider: ${String(error)}`);
  }
}

const requireSecretProvider = (path: string): SecretProvider => {
  if (!secretProvider) {
    throw new SecretProviderError(
      `Secret provider is not configured but secret path '${path}' was requested`,
    );
  }
  return secretProvider;
};

const resolveJwtPublicKey = async (): Promise<string | undefined> => {
  const secretPath = process.env.AION_JWT_SECRET_PATH;
  if (!secretPath) {
    return process.env.AION_JWT_PUBLIC_KEY;
  }
  const provider = requireSecretProvider(secretPath);
  const payload = await provider.getSecret(secretPath);
  if (typeof payload === 'string') {
    return payload;
  }
  if (typeof payload.public_key === 'string') {
    return payload.public_key;
  }
  if (typeof payload.jwt === 'string') {
    return payload.jwt;
  }
  return undefined;
};

const resolveAdminToken = async (): Promise<string> => {
  const secretPath = process.env.AION_ADMIN_TOKEN_SECRET_PATH;
  if (!secretPath) {
    return process.env.AION_ADMIN_TOKEN || process.env.AUTH_TOKEN || '';
  }
  const provider = requireSecretProvider(secretPath);
  const payload = await provider.getSecret(secretPath);
  if (typeof payload === 'string') {
    return payload;
  }
  if (typeof payload.token === 'string') {
    return payload.token;
  }
  if (typeof payload.value === 'string') {
    return payload.value;
  }
  return '';
};

const resolveApiKeys = async (): Promise<Record<string, { roles: string[]; tenant?: string }>> => {
  const secretPath = process.env.AION_GATEWAY_API_KEYS_SECRET_PATH;
  if (!secretPath) {
    return parseApiKeysString(process.env.AION_GATEWAY_API_KEYS);
  }
  const provider = requireSecretProvider(secretPath);
  const payload = await provider.getSecret(secretPath);
  return parseApiKeysSecret(payload);
};

async function buildGatewayConfig(): Promise<GatewayConfig> {
  const [apiKeys, jwtPublicKey, adminToken] = await Promise.all([
    resolveApiKeys(),
    resolveJwtPublicKey(),
    resolveAdminToken(),
  ]);

  return {
    port: Number(process.env.AION_GATEWAY_PORT || 8080),
    host: process.env.AION_GATEWAY_HOST || '0.0.0.0',
    controlGrpcEndpoint: process.env.AION_CONTROL_GRPC || 'control:50051',
    controlBaseUrl: process.env.AION_CONTROL_BASE || 'http://control:8000',
    redisUrl: process.env.AION_REDIS_URL || 'redis://redis:6379',
    apiKeys,
    jwtPublicKey,
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
      certPath: process.env.AION_TLS_CERT || 'config/certs/gateway-client.pem',
      keyPath: process.env.AION_TLS_KEY || 'config/certs/gateway-client-key.pem',
      caPaths: parseCaPaths(process.env.AION_TLS_CA_CHAIN || 'config/certs/dev-ca.pem'),
      requireMtls: process.env.AION_TLS_REQUIRE_MTLS !== 'false',
    },
    telemetry: {
      enabled: process.env.AION_OTEL_ENABLED === 'true',
      serviceName: process.env.AION_SERVICE_NAME || 'aionos-gateway',
    },
    profile,
    featureSeal,
    adminToken,
    devKernel: {
      enabled: process.env.AION_DEV_KERNEL_ENABLED !== 'false',
      url: process.env.AION_DEV_KERNEL_URL || 'http://dev-kernel:9100/kernel',
      profile: process.env.AION_DEV_KERNEL_PROFILE || 'dev-qwen-coder',
    },
  };
}

export const gatewayConfig: GatewayConfig = await buildGatewayConfig();
