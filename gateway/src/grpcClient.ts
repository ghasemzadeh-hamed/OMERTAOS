import { credentials, loadPackageDefinition } from '@grpc/grpc-js';
import { loadSync } from '@grpc/proto-loader';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { gatewayConfig } from './config.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const protoPath = path.resolve(__dirname, '../../protos/aion/v1/tasks.proto');

const packageDefinition = loadSync(protoPath, {
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const loaded = loadPackageDefinition(packageDefinition) as unknown as {
  aion: {
    v1: {
      AionTasks: new (addr: string, creds: ReturnType<typeof credentials.createInsecure>) => any;
    };
  };
};

export const createControlClient = () => {
  const { controlGrpcEndpoint } = gatewayConfig;
  return new loaded.aion.v1.AionTasks(controlGrpcEndpoint, credentials.createInsecure());
};
