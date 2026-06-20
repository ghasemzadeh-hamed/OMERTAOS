export class SecretProviderError extends Error {
  constructor(message) {
    super(message);
    this.name = 'SecretProviderError';
  }
}

export class SecretProvider {
  constructor(options = {}) {
    this.mode = options.mode || 'local';
  }

  async getSecret(path) {
    const key = String(path || '').replace(/^env:\/\//, '').replace(/^env:/, '');
    if (!key) {
      throw new SecretProviderError('Secret path is required');
    }
    const value = process.env[key];
    if (value === undefined) {
      throw new SecretProviderError(`Secret '${key}' is not defined`);
    }
    return value;
  }
}

export default SecretProvider;
