import { SecretProvider, SecretProviderError } from '@aionos/secret-provider';

export interface ConsoleSecrets {
  adminToken: string;
}

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

const ensureSecretProvider = (path: string): SecretProvider => {
  if (!secretProvider) {
    throw new SecretProviderError(
      `Secret provider is not configured but secret path '${path}' was requested`,
    );
  }
  return secretProvider;
};

const loadConsoleSecrets = async (): Promise<ConsoleSecrets> => {
  const secretPath = process.env.AION_ADMIN_TOKEN_SECRET_PATH;
  if (!secretPath) {
    return {
      adminToken: process.env.AION_ADMIN_TOKEN || process.env.NEXT_PUBLIC_SETUP_TOKEN || '',
    };
  }
  const provider = ensureSecretProvider(secretPath);
  const payload = await provider.getSecret(secretPath);
  if (typeof payload === 'string') {
    return { adminToken: payload };
  }
  if (typeof payload.token === 'string') {
    return { adminToken: payload.token };
  }
  if (typeof payload.value === 'string') {
    return { adminToken: payload.value };
  }
  return { adminToken: '' };
};

const consoleSecretsPromise = loadConsoleSecrets();

export const getConsoleSecrets = async (): Promise<ConsoleSecrets> => consoleSecretsPromise;
