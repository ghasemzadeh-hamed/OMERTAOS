export class SecretProviderError extends Error {
  constructor(message?: string);
}

export class SecretProvider {
  constructor(options?: Record<string, unknown>);
  getSecret(path: string): Promise<Record<string, unknown> | string>;
}

export default SecretProvider;
