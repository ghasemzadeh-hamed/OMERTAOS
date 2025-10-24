import { credentials, loadPackageDefinition } from '@grpc/grpc-js';
import { loadSync } from '@grpc/proto-loader';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadTlsArtifacts } from '../config/tls.js';
import { gatewayConfig } from '../config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const protoPath = path.resolve(__dirname, '../../../protos/aion/v1/tasks.proto');

const packageDefinition = loadSync(protoPath, {
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const loaded = loadPackageDefinition(packageDefinition) as unknown as {
  aion: {
    v1: {
      AionTasks: new (addr: string, creds: ReturnType<typeof credentials.createInsecure>, options?: Record<string, unknown>) => any;
    };
  };
};

export const createControlClient = () => {
  const { controlGrpcEndpoint, environment } = gatewayConfig;
  if (environment === 'production') {
    const tls = loadTlsArtifacts();
    const rootCerts = tls.ca?.length ? Buffer.concat(tls.ca) : undefined;
    const secureCreds = credentials.createSsl(rootCerts, tls.key, tls.cert);
    const options = tls.requestClientCert
      ? { 'grpc.ssl_target_name_override': process.env.AION_CONTROL_TLS_NAME || 'control.aionos.local' }
      : undefined;
    return new loaded.aion.v1.AionTasks(controlGrpcEndpoint, secureCreds, options);
  }
  return new loaded.aion.v1.AionTasks(controlGrpcEndpoint, credentials.createInsecure());
};
