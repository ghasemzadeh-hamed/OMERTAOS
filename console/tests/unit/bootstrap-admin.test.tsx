import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@prisma/client', () => ({
  PrismaClient: vi.fn(() => ({})),
  Role: { ADMIN: 'ADMIN' },
}));

import { bootstrapConsole, resolveAdminCredentials } from '../../scripts/bootstrap-admin.ts';

beforeEach(() => {
  process.env.DATABASE_URL = 'postgresql://test:test@127.0.0.1:5432/test';
});

afterEach(() => {
  delete process.env.DATABASE_URL;
  delete process.env.CONSOLE_ADMIN_EMAIL;
  delete process.env.CONSOLE_ADMIN_PASSWORD;
  delete process.env.CONSOLE_BOOTSTRAP_CHECK;
});

describe('native console bootstrap', () => {
  it('rejects missing or default credentials', () => {
    expect(() => resolveAdminCredentials()).toThrow(/CONSOLE_ADMIN_EMAIL/);
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'admin123';
    expect(() => resolveAdminCredentials()).toThrow(/at least 16/);
  });

  it('is idempotent when the configured admin already exists', async () => {
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'strong-native-password';
    const client = {
      systemState: { upsert: vi.fn() },
      user: {
        count: vi.fn().mockResolvedValue(1),
        findUnique: vi.fn().mockResolvedValue({ role: 'ADMIN' }),
        create: vi.fn(),
      },
    } as any;

    await bootstrapConsole(client);
    expect(client.user.create).not.toHaveBeenCalled();
    expect(client.systemState.upsert).toHaveBeenCalledOnce();
  });

  it('fails closed when unrelated users already exist', async () => {
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'strong-native-password';
    const client = {
      systemState: { upsert: vi.fn() },
      user: {
        count: vi.fn().mockResolvedValue(1),
        findUnique: vi.fn().mockResolvedValue(null),
        create: vi.fn(),
      },
    } as any;

    await expect(bootstrapConsole(client)).rejects.toThrow(/refusing to add or modify/);
    expect(client.user.create).not.toHaveBeenCalled();
  });
});
