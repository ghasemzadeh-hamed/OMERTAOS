import fs from 'node:fs';
import path from 'node:path';
import { gatewayConfig } from '../config.js';

export interface TlsArtifacts {
  key?: Buffer;
  cert?: Buffer;
  ca?: Buffer[];
  enabled: boolean;
  requestClientCert: boolean;
}

const readFileIfExists = (filePath?: string): Buffer | undefined => {
  if (!filePath) {
    return undefined;
  }
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    throw new Error(`TLS file not found: ${resolved}`);
  }
  return fs.readFileSync(resolved);
};

export const loadTlsArtifacts = (): TlsArtifacts => {
  if (gatewayConfig.environment !== 'production' || !gatewayConfig.tls.enabled) {
    return { enabled: false, requestClientCert: false };
  }
  const key = readFileIfExists(gatewayConfig.tls.keyPath);
  const cert = readFileIfExists(gatewayConfig.tls.certPath);
  const caPaths = [...(gatewayConfig.tls.caPaths ?? [])];
  if (gatewayConfig.tls.mtlsCaPath) {
    caPaths.push(gatewayConfig.tls.mtlsCaPath);
  }
  const ca = caPaths.map((p) => readFileIfExists(p)).filter(Boolean) as Buffer[];
  if (!key || !cert) {
    throw new Error('TLS key and cert are required in production');
  }
  return {
    key,
    cert,
    ca,
    enabled: true,
    requestClientCert: gatewayConfig.tls.requireMtls,
  };
};
