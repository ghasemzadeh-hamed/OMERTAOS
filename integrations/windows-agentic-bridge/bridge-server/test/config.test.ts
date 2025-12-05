import { describe, expect, it } from 'vitest';
import { loadConfig } from '../src/config.js';

describe('loadConfig', () => {
  it('throws when token missing', () => {
    expect(() => loadConfig({} as any)).toThrowError();
  });

  it('returns defaults', () => {
    const cfg = loadConfig({ OMERTA_ADMIN_TOKEN: 't' } as any);
    expect(cfg.gatewayUrl).toContain('http://localhost');
    expect(cfg.adminToken).toBe('t');
  });
});
