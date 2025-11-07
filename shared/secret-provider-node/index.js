/* eslint-disable no-console */
const DEFAULT_MOUNT = 'kv';

class SecretProviderError extends Error {}

export class SecretProvider {
  constructor({ vaultAddr, authMethod, namespace } = {}) {
    this.vaultAddr = (vaultAddr || process.env.VAULT_ADDR || '').trim();
    if (!this.vaultAddr) {
      throw new SecretProviderError('VAULT_ADDR must be defined');
    }

    this.authMethod = (authMethod || process.env.VAULT_AUTH_METHOD || 'token').toLowerCase();
    this.namespace = namespace || process.env.VAULT_NAMESPACE;
    this.token = null;
    this._authPromise = null;
  }

  async ensureAuthenticated() {
    if (this.token) {
      return this.token;
    }
    if (!this._authPromise) {
      this._authPromise = this.authenticate();
    }
    this.token = await this._authPromise;
    return this.token;
  }

  async authenticate() {
    if (this.authMethod === 'token') {
      const token = process.env.VAULT_TOKEN;
      if (!token) {
        throw new SecretProviderError('VAULT_TOKEN must be set for token authentication');
      }
      return token;
    }
    if (this.authMethod === 'approle') {
      const roleId = process.env.VAULT_APPROLE_ROLE_ID;
      const secretId = process.env.VAULT_APPROLE_SECRET_ID;
      if (!roleId || !secretId) {
        throw new SecretProviderError(
          'VAULT_APPROLE_ROLE_ID and VAULT_APPROLE_SECRET_ID must be provided for AppRole auth',
        );
      }
      const url = new URL('/v1/auth/approle/login', this.vaultAddr);
      const headers = { 'content-type': 'application/json' };
      if (this.namespace) {
        headers['X-Vault-Namespace'] = this.namespace;
      }
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify({ role_id: roleId, secret_id: secretId }),
      });
      if (!response.ok) {
        const body = await response.text();
        throw new SecretProviderError(`Vault approle login failed: ${response.status} ${body}`);
      }
      const payload = await response.json();
      const token = payload?.auth?.client_token;
      if (!token) {
        throw new SecretProviderError('Vault approle login did not return a client token');
      }
      return token;
    }
    throw new SecretProviderError(`Unsupported VAULT_AUTH_METHOD '${this.authMethod}'`);
  }

  splitPath(path) {
    const cleaned = String(path || '').replace(/^\/+|\/+$/g, '');
    if (!cleaned) {
      throw new SecretProviderError('Secret path may not be empty');
    }
    const segments = cleaned.split('/');
    if (segments.length === 1) {
      return { mount: DEFAULT_MOUNT, secretPath: segments[0] };
    }
    if (segments.length >= 3 && segments[1] === 'data') {
      return { mount: segments[0], secretPath: segments.slice(2).join('/') };
    }
    return { mount: segments[0], secretPath: segments.slice(1).join('/') };
  }

  async getSecret(path) {
    const token = await this.ensureAuthenticated();
    const { mount, secretPath } = this.splitPath(path);
    const url = new URL(`/v1/${mount}/data/${secretPath}`, this.vaultAddr);
    const headers = { 'X-Vault-Token': token };
    if (this.namespace) {
      headers['X-Vault-Namespace'] = this.namespace;
    }
    const response = await fetch(url, { headers });
    if (!response.ok) {
      const body = await response.text();
      throw new SecretProviderError(`Vault secret fetch failed: ${response.status} ${body}`);
    }
    const payload = await response.json();
    const data = payload?.data?.data;
    if (!data || typeof data !== 'object') {
      throw new SecretProviderError('Vault secret payload was empty');
    }
    if (Object.prototype.hasOwnProperty.call(data, 'value') && typeof data.value === 'string') {
      return data.value;
    }
    return data;
  }
}

export { SecretProviderError };
