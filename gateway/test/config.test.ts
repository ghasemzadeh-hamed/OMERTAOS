import { afterEach, describe, expect, it, vi } from 'vitest';

describe('gateway configuration hardening', () => {
  afterEach(() => {
    vi.resetModules();
    vi.unstubAllEnvs();
  });

  it('defaults to wildcard origins without credentials outside production', async () => {
    vi.stubEnv('AION_ENV', 'development');

    const { buildGatewayConfig } = await import('../src/config.js');
    const config = await buildGatewayConfig();

    expect(config.corsOrigins).toEqual(['*']);
    expect(config.corsAllowCredentials).toBe(false);
  });

  it('disables CORS credentials when wildcard origin is used outside production', async () => {
    vi.stubEnv('AION_CORS_ORIGINS', '*');
    vi.stubEnv('AION_ENV', 'development');

    const { buildGatewayConfig } = await import('../src/config.js');
    const config = await buildGatewayConfig();

    expect(config.corsOrigins).toEqual(['*']);
    expect(config.corsAllowCredentials).toBe(false);
  });

  it('rejects wildcard origins in production', async () => {
    vi.stubEnv('AION_CORS_ORIGINS', '*');
    vi.stubEnv('AION_ENV', 'production');

    await expect(async () => {
      const { buildGatewayConfig } = await import('../src/config.js');
      await buildGatewayConfig();
    }).rejects.toThrow(/AION_CORS_ORIGINS/);
  });

  it('allows explicit origins and enables credentials', async () => {
    vi.stubEnv('AION_CORS_ORIGINS', 'https://example.com,https://api.example.com');
    vi.stubEnv('AION_ENV', 'production');

    const { buildGatewayConfig } = await import('../src/config.js');
    const config = await buildGatewayConfig();

    expect(config.corsOrigins).toEqual([
      'https://example.com',
      'https://api.example.com',
    ]);
    expect(config.corsAllowCredentials).toBe(true);
  });

  it('rejects wildcard origin combined with explicit origins', async () => {
    vi.stubEnv('AION_CORS_ORIGINS', '*,https://example.com');
    vi.stubEnv('AION_ENV', 'development');

    await expect(async () => {
      const { buildGatewayConfig } = await import('../src/config.js');
      await buildGatewayConfig();
    }).rejects.toThrow(/Wildcard CORS origin/);
  });
});
