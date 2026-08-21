import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const userUpsert = vi.fn();
const completeSetup = vi.fn();
const hash = vi.fn();

vi.mock('@/lib/prisma', () => ({
  prisma: {
    user: {
      upsert: userUpsert,
    },
  },
}));

vi.mock('@/lib/setup', () => ({
  completeSetup,
}));

vi.mock('bcrypt', () => ({
  default: {
    hash,
  },
}));

describe('setup bootstrap route', () => {
  beforeEach(() => {
    vi.resetModules();
    userUpsert.mockReset();
    completeSetup.mockReset();
    hash.mockReset().mockResolvedValue('hashed-password');
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: vi.fn().mockResolvedValue('{"ok":true}'),
    }) as any;
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('persists the setup admin credentials before completing setup', async () => {
    const { POST } = await import('@/app/api/system/setup/bootstrap/route');

    const response = await POST(
      new Request('http://localhost/api/system/setup/bootstrap', {
        method: 'POST',
        body: JSON.stringify({
          username: 'admin',
          password: 'chosen-password',
          profile: 'user',
          encryptData: true,
        }),
      }),
    );

    await expect(response.json()).resolves.toEqual({ ok: true });
    expect(hash).toHaveBeenCalledWith('chosen-password', 12);
    expect(userUpsert).toHaveBeenCalledWith({
      where: { email: 'admin@local' },
      update: {
        password: 'hashed-password',
        role: 'ADMIN',
        name: 'admin',
      },
      create: {
        email: 'admin@local',
        password: 'hashed-password',
        role: 'ADMIN',
        name: 'admin',
      },
    });
    expect(completeSetup).toHaveBeenCalledOnce();
  });

  it('does not mark setup complete when the gateway bootstrap fails', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      text: vi.fn().mockResolvedValue('{"detail":"gateway failed"}'),
    }) as any;
    const { POST } = await import('@/app/api/system/setup/bootstrap/route');

    const response = await POST(
      new Request('http://localhost/api/system/setup/bootstrap', {
        method: 'POST',
        body: JSON.stringify({
          username: 'admin',
          password: 'chosen-password',
          profile: 'user',
          encryptData: true,
        }),
      }),
    );

    expect(response.status).toBe(502);
    await expect(response.json()).resolves.toEqual({ error: 'gateway failed' });
    expect(userUpsert).not.toHaveBeenCalled();
    expect(completeSetup).not.toHaveBeenCalled();
  });
});
