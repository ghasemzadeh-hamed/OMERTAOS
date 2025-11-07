import { gatewayConfig } from '../config.js';

export interface TlsArtifacts {
  key?: Buffer;
  cert?: Buffer;
  ca?: Buffer[];
  enabled: boolean;
  requestClientCert: boolean;
}

export const loadTlsArtifacts = (): TlsArtifacts => {
  const shouldEnable = gatewayConfig.tls.requireMtls || gatewayConfig.environment === 'production';
  if (!shouldEnable) {
    return { enabled: false, requestClientCert: false };
  }
  const keyPem = gatewayConfig.tls.keyPem;
  const certPem = gatewayConfig.tls.certPem;
  const caPem = gatewayConfig.tls.caPem;
  if (!keyPem || !certPem) {
    throw new Error('TLS key and certificate must be available from Vault or environment');
  }
  return {
    key: Buffer.from(keyPem, 'utf8'),
    cert: Buffer.from(certPem, 'utf8'),
    ca: caPem?.map((entry) => Buffer.from(entry, 'utf8')),
    enabled: true,
    requestClientCert: gatewayConfig.tls.requireMtls,
  };
};
