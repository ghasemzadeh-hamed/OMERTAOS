import { describe, expect, it, beforeEach, afterEach, vi } from 'vitest';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import * as grpcCredentials from '@grpc/grpc-js';

const originalEnv = { ...process.env };
let tmpDir: string;

describe('gRPC mTLS configuration', () => {
  beforeEach(() => {
    vi.resetModules();
    tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'aionos-tls-'));
    const keyPath = path.join(tmpDir, 'key.pem');
    const certPath = path.join(tmpDir, 'cert.pem');
    const caPath = path.join(tmpDir, 'ca.pem');
    fs.writeFileSync(keyPath, 'test-key');
    fs.writeFileSync(certPath, 'test-cert');
    fs.writeFileSync(caPath, 'test-ca');
    process.env.NODE_ENV = 'production';
    process.env.AION_TLS_ENABLED = 'true';
    process.env.AION_CONTROL_GRPC = 'localhost:50051';
    process.env.AION_TLS_CERT_PATH = certPath;
    process.env.AION_TLS_KEY_PATH = keyPath;
    process.env.AION_TLS_CA_CHAIN = caPath;
    process.env.AION_MTLS_ENABLED = 'true';
  });

  afterEach(() => {
    for (const key of Object.keys(process.env)) {
      if (!(key in originalEnv)) {
        delete process.env[key];
      }
    }
    Object.assign(process.env, originalEnv);
    if (tmpDir && fs.existsSync(tmpDir)) {
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
    vi.restoreAllMocks();
  });

  it('creates secure credentials when TLS enabled', async () => {
    const sslSpy = vi.spyOn(grpcCredentials.credentials, 'createSsl').mockReturnValue({} as any);
    const insecureSpy = vi.spyOn(grpcCredentials.credentials, 'createInsecure');
    const { createControlClient } = await import('../../gateway/src/server/grpc.js');
    createControlClient();
    expect(sslSpy).toHaveBeenCalled();
    expect(insecureSpy).not.toHaveBeenCalled();
  });
});
