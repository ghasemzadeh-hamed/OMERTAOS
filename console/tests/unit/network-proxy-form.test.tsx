import { describe, expect, it } from 'vitest';

import { validateProxyForm } from '../../lib/network/proxyValidation';

const baseForm = {
  name: 'Provider proxy',
  type: 'http',
  enabled: true,
  scope: 'ai_providers',
  host: 'proxy.local',
  port: '8080',
  transport: '',
  security: '',
  sni: '',
  flow: '',
  path: '',
  fallback_direct: false,
  health_check_url: '',
  secrets: {
    uuid: '',
    password: '',
    private_key: '',
    public_key: '',
    short_id: '',
  },
} as const;

describe('network proxy form validation', () => {
  it('requires host and port for non-direct profiles', () => {
    expect(validateProxyForm({ ...baseForm, host: '' } as any)).toBe('Host is required for proxy profiles');
    expect(validateProxyForm({ ...baseForm, port: '70000' } as any)).toBe('Port must be between 1 and 65535');
  });

  it('allows direct profiles without endpoint fields', () => {
    expect(validateProxyForm({ ...baseForm, type: 'direct', host: '', port: '' } as any)).toBeNull();
  });

  it('keeps VLESS secrets write-only when editing', () => {
    const form = { ...baseForm, type: 'vless', secrets: { ...baseForm.secrets, uuid: '' } };
    expect(validateProxyForm(form as any, true)).toBeNull();
    expect(validateProxyForm(form as any, false)).toBe('VLESS UUID is required');
  });
});


