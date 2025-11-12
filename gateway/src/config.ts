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

type GatewayEnvironment = 'development' | 'test' | 'production';

export interface GatewayConfig {
  port: number;
  host: string;
  controlGrpcEndpoint: string;
  controlBaseUrl: string;
  redisUrl: string;
  selfEvolving: {
    enabled: boolean;
    modelRegistryUrl: string;
    memoryUrl: string;
    defaultChannel: string;
  };
  apiKeys: Record<string, { roles: string[]; tenant?: string }>;
  jwtPublicKey: string | undefined;
  corsOrigins: string[];
  corsAllowCredentials: boolean;
  rateLimit: {
    max: number;
    timeWindow: string;
    perIp: number;
  };
  idempotencyTtlSeconds: number;
  environment: GatewayEnvironment;
  tls: {
    requireMtls: boolean;
    secretPath?: string;
    clientCaSecretPath?: string;
    certPem?: string;
    keyPem?: string;
    caPem?: string[];
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

const profile = (process.env.AION_PROFILE || 'user').toLowerCase() as GatewayConfig['profile'];
const featureSeal = process.env.FEATURE_SEAL === '1' || profile === 'enterprise-vip';

const parseCorsOrigins = (raw: string | undefined): string[] => {
  if (!raw) {
    return [];
  }
  return raw
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean);
};

const normaliseCorsOrigins = (origins: string[]): string[] => {
  return Array.from(new Set(origins));
};

const resolveCorsConfiguration = (
  rawOrigins: string | undefined,
  environment: GatewayEnvironment,
): { origins: string[]; allowCredentials: boolean } => {
  const parsedOrigins = parseCorsOrigins(rawOrigins);
  const origins = normaliseCorsOrigins(parsedOrigins);
  if (origins.length === 0) {
    if (environment === 'production') {
      throw new Error(
        'AION_CORS_ORIGINS must be configured with one or more allowed origins in production environments.',
      );
    }
    return { origins: ['*'], allowCredentials: false };
  }

  if (origins.includes('*')) {
    if (origins.length > 1) {
      throw new Error(
        'Wildcard CORS origin (*) cannot be combined with explicit origins. Remove the wildcard or list specific origins.',
      );
    }
    if (environment === 'production') {
      throw new Error(
        'Wildcard CORS origins (*) are not permitted in production. Set explicit origins via AION_CORS_ORIGINS.',
      );
    }
    return { origins: ['*'], allowCredentials: false };
  }

  return { origins, allowCredentials: true };
};

let secretProvider: SecretProvider | null = null;
if (process.env.AION_VAULT_ADDR || process.env.VAULT_ADDR) {
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

const takeString = (candidate: unknown): string | undefined => {
  if (typeof candidate === 'string' && candidate.trim()) {
    return candidate.trim();
  }
  return undefined;
};

const normalisePemArray = (value: unknown): string[] | undefined => {
  if (!value) {
    return undefined;
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    return trimmed ? [trimmed] : undefined;
  }
  if (Array.isArray(value)) {
    const entries = value
      .map((item) => (typeof item === 'string' ? item.trim() : ''))
      .filter((item) => item.length > 0);
    return entries.length ? entries : undefined;
  }
  return undefined;
};

const resolveTlsMaterials = async (): Promise<{
  secretPath?: string;
  clientCaSecretPath?: string;
  certPem?: string;
  keyPem?: string;
  caPem?: string[];
}> => {
  const secretPath = process.env.AION_TLS_SECRET_PATH;
  const clientCaSecretPath = process.env.AION_TLS_CLIENT_CA_SECRET_PATH;
  let certPem = takeString(process.env.AION_TLS_CERT_PEM || process.env.AION_TLS_CERT);
  let keyPem = takeString(process.env.AION_TLS_KEY_PEM || process.env.AION_TLS_KEY);
  let caPem = normalisePemArray(process.env.AION_TLS_CA_PEM || process.env.AION_TLS_CA_CHAIN);

  if (secretPath) {
    const provider = requireSecretProvider(secretPath);
    const payload = await provider.getSecret(secretPath);
    if (typeof payload === 'string') {
      throw new SecretProviderError(
        `TLS secret '${secretPath}' must be an object with certificate and private_key fields`,
      );
    }
    certPem =
      takeString(payload.certificate) ||
      takeString(payload.cert) ||
      takeString(payload.public_cert) ||
      certPem;
    keyPem = takeString(payload.private_key) || takeString(payload.key) || keyPem;
    caPem =
      normalisePemArray(payload.ca_chain) ||
      normalisePemArray(payload.ca) ||
      normalisePemArray(payload.certificate_authority) ||
      caPem;
  }

  if (clientCaSecretPath) {
    const provider = requireSecretProvider(clientCaSecretPath);
    const payload = await provider.getSecret(clientCaSecretPath);
    if (typeof payload === 'string') {
      caPem = normalisePemArray(payload) || caPem;
    } else {
      caPem =
        normalisePemArray(payload.ca_chain) ||
        normalisePemArray(payload.ca) ||
        normalisePemArray(payload.certificate) ||
        caPem;
    }
  }

  return {
    secretPath,
    clientCaSecretPath,
    certPem,
    keyPem,
    caPem,
  };
};

export async function buildGatewayConfig(): Promise<GatewayConfig> {
  const [apiKeys, jwtPublicKey, adminToken, tlsMaterials] = await Promise.all([
    resolveApiKeys(),
    resolveJwtPublicKey(),
    resolveAdminToken(),
    resolveTlsMaterials(),
  ]);

  const environment = (process.env.AION_ENV || process.env.NODE_ENV || 'development') as GatewayEnvironment;
  const cors = resolveCorsConfiguration(process.env.AION_CORS_ORIGINS, environment);

  return {
    port: Number(process.env.AION_GATEWAY_PORT || 8080),
    host: process.env.AION_GATEWAY_HOST || '0.0.0.0',
    controlGrpcEndpoint: process.env.AION_CONTROL_GRPC || 'control:50051',
    controlBaseUrl: process.env.AION_CONTROL_BASE || 'http://control:8000',
    redisUrl: process.env.AION_REDIS_URL || 'redis://redis:6379',
    selfEvolving: {
      enabled:
        process.env.AION_SELF_EVOLVING_ENABLED !== 'false' &&
        process.env.AION_SELF_EVOLVING_ENABLED !== '0',
      modelRegistryUrl: process.env.AION_MODEL_REGISTRY_URL || 'http://aion-model-registry:8081',
      memoryUrl: process.env.AION_MEMORY_URL || 'http://aion-memory:8080',
      defaultChannel: process.env.AION_SELF_EVOLVING_CHANNEL || 'enterprise',
    },
    apiKeys,
    jwtPublicKey,
    corsOrigins: cors.origins,
    corsAllowCredentials: cors.allowCredentials,
    rateLimit: {
      max: Number(process.env.AION_RATE_LIMIT_MAX || 60),
      timeWindow: process.env.AION_RATE_LIMIT_WINDOW || '1 minute',
      perIp: Number(process.env.AION_RATE_LIMIT_PER_IP || 30),
    },
    idempotencyTtlSeconds: Number(process.env.AION_IDEMPOTENCY_TTL || 900),
    environment,
    tls: {
      requireMtls:
        process.env.AION_TLS_REQUIRE_MTLS === '1' ||
        process.env.AION_TLS_REQUIRE_MTLS === 'true' ||
        process.env.AION_TLS_REQUIRE_MTLS === 'yes' ||
        process.env.AION_TLS_REQUIRE_MTLS === 'on' ||
        profile === 'enterprise-vip',
      secretPath: tlsMaterials.secretPath,
      clientCaSecretPath: tlsMaterials.clientCaSecretPath,
      certPem: tlsMaterials.certPem,
      keyPem: tlsMaterials.keyPem,
      caPem: tlsMaterials.caPem,
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
