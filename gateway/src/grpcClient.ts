import { credentials, loadPackageDefinition } from '@grpc/grpc-js';
import { loadSync } from '@grpc/proto-loader';
import { gatewayConfig } from './config.js';
import { resolveProtoPath } from './protoPath.js';

const protoPath = resolveProtoPath('aion/v1/tasks.proto');

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
