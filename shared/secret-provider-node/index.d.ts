export interface SecretProviderOptions {
  vaultAddr?: string;
  authMethod?: string;
  namespace?: string;
}

export class SecretProviderError extends Error {}

export class SecretProvider {
  constructor(options?: SecretProviderOptions);
  getSecret(path: string): Promise<Record<string, unknown> | string>;
}
