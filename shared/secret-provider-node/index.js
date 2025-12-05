/* eslint-disable no-console */
const DEFAULT_MOUNT =
  process.env.AION_VAULT_KV_MOUNT || process.env.VAULT_KV_MOUNT || 'secret';

const normaliseMode = (mode) => (mode || process.env.SECRET_PROVIDER_MODE || 'vault').trim().toLowerCase();

const takeEnvToken = () => {
  return (
    process.env.AION_DEV_ADMIN_TOKEN ||
    process.env.AION_GATEWAY_ADMIN_TOKEN ||
    process.env.AION_ADMIN_TOKEN ||
    process.env.NEXT_PUBLIC_SETUP_TOKEN ||
    ''
  ).trim();
};

const normaliseEnvSecretKey = (path) => {
  const trimmed = String(path ?? '').trim();
  if (trimmed.startsWith('env://')) {
    return trimmed.slice('env://'.length);
  }
  if (trimmed.startsWith('env:')) {
    return trimmed.slice('env:'.length);
  }
  return trimmed;
};

class SecretProviderError extends Error {}

export class SecretProvider {
  constructor({ vaultAddr, authMethod, namespace, kvMount, mode } = {}) {
    this.mode = normaliseMode(mode);
    this.localSecrets = new Map();

    if (this.mode === 'local') {
      const devToken = takeEnvToken();
      if (devToken) {
        this.localSecrets.set('secret/aionos/dev/admin-token', devToken);
      }
      this.namespace = '';
      this.kvMount = DEFAULT_MOUNT;
      this.token = null;
      this._authPromise = null;
      return;
    }

    this.vaultAddr = (
      vaultAddr || process.env.AION_VAULT_ADDR || process.env.VAULT_ADDR || ''
    ).trim();
    if (!this.vaultAddr) {
      throw new SecretProviderError('AION_VAULT_ADDR must be defined');
    }

    this.authMethod = (
      authMethod ||
      process.env.AION_VAULT_AUTH_METHOD ||
      process.env.VAULT_AUTH_METHOD ||
      'token'
    ).toLowerCase();
    this.namespace =
      namespace || process.env.AION_VAULT_NAMESPACE || process.env.VAULT_NAMESPACE;
    this.kvMount = (
      kvMount ||
      process.env.AION_VAULT_KV_MOUNT ||
      process.env.VAULT_KV_MOUNT ||
      DEFAULT_MOUNT
    )
      .trim()
      .replace(/^\/+|\/+$/g, '') || DEFAULT_MOUNT;
    this.token = null;
    this._authPromise = null;
  }

  async ensureAuthenticated() {
    if (this.mode === 'local') {
      return '';
    }
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
      const token = process.env.AION_VAULT_TOKEN || process.env.VAULT_TOKEN;
      if (!token) {
        throw new SecretProviderError(
          'AION_VAULT_TOKEN must be set for token authentication',
        );
      }
      return token;
    }
    if (this.authMethod === 'approle') {
      const roleId =
        process.env.AION_VAULT_APPROLE_ROLE_ID || process.env.VAULT_APPROLE_ROLE_ID;
      const secretId =
        process.env.AION_VAULT_APPROLE_SECRET_ID || process.env.VAULT_APPROLE_SECRET_ID;
      if (!roleId || !secretId) {
        throw new SecretProviderError(
          'AION_VAULT_APPROLE_ROLE_ID and AION_VAULT_APPROLE_SECRET_ID must be provided for AppRole auth',
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
    throw new SecretProviderError(
      `Unsupported AION_VAULT_AUTH_METHOD '${this.authMethod}'`,
    );
  }

  splitPath(path) {
    const cleaned = String(path || '').replace(/^\/+|\/+$/g, '');
    if (!cleaned) {
      throw new SecretProviderError('Secret path may not be empty');
    }
    const segments = cleaned.split('/');
    if (segments.length === 1) {
      return { mount: this.kvMount, secretPath: segments[0] };
    }
    if (segments.length >= 3 && segments[1] === 'data') {
      return { mount: segments[0], secretPath: segments.slice(2).join('/') };
    }
    return { mount: segments[0], secretPath: segments.slice(1).join('/') };
  }

  async getSecret(path) {
    const cleaned = String(path || '').trim();
    if (this.mode === 'local') {
      const normalised = cleaned.replace(/^\/+|\/+$/g, '');
      if (!normalised) {
        throw new SecretProviderError('Secret path may not be empty');
      }
      if (this.localSecrets.has(normalised)) {
        return this.localSecrets.get(normalised);
      }
      if (normalised.startsWith('env:') || normalised.startsWith('env://')) {
        const envKey = normaliseEnvSecretKey(normalised);
        const value = envKey ? process.env[envKey] : undefined;
        if (value === undefined) {
          throw new SecretProviderError(`Env secret '${envKey}' is not defined in process.env`);
        }
        return value;
      }
      if (normalised === 'secret/aionos/dev/admin-token') {
        throw new SecretProviderError(
          "Dev admin token is not configured. Set AION_DEV_ADMIN_TOKEN or AION_ADMIN_TOKEN to continue setup.",
        );
      }
      throw new SecretProviderError(
        `Local secret '${normalised}' was not found. Provide it via process.env or switch SECRET_PROVIDER_MODE.`,
      );
    }

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
