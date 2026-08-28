import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@prisma/client', () => ({
  PrismaClient: class MockPrismaClient {},
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
  delete process.env.CONSOLE_ADMIN_PASSWORD_MIN_LENGTH;
  delete process.env.CONSOLE_ADMIN_PASSWORD_MAX_LENGTH;
  delete process.env.CONSOLE_BOOTSTRAP_CHECK;
});

describe('native console bootstrap', () => {
  it('rejects missing or default credentials', () => {
    expect(() => resolveAdminCredentials()).toThrow(/CONSOLE_ADMIN_EMAIL/);
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'admin123';
    expect(() => resolveAdminCredentials()).toThrow(/between 8 and 32/);
    process.env.CONSOLE_ADMIN_PASSWORD = 'x'.repeat(33);
    expect(() => resolveAdminCredentials()).toThrow(/between 8 and 32/);
  });

  it('accepts configured password bounds without lowering the eight-character floor', () => {
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'strong-native-password';
    process.env.CONSOLE_ADMIN_PASSWORD_MAX_LENGTH = '32';
    expect(resolveAdminCredentials().password).toBe('strong-native-password');

    process.env.CONSOLE_ADMIN_PASSWORD_MIN_LENGTH = '7';
    expect(() => resolveAdminCredentials()).toThrow(/cannot be less than 8/);
    process.env.CONSOLE_ADMIN_PASSWORD_MIN_LENGTH = '8';
    process.env.CONSOLE_ADMIN_PASSWORD_MAX_LENGTH = 'not-a-number';
    expect(() => resolveAdminCredentials()).toThrow(/must be an integer/);
  });

  it('is idempotent when the configured admin already exists', async () => {
    process.env.CONSOLE_ADMIN_EMAIL = 'admin@example.test';
    process.env.CONSOLE_ADMIN_PASSWORD = 'StrongPass123!';
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
    process.env.CONSOLE_ADMIN_PASSWORD = 'StrongPass123!';
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
