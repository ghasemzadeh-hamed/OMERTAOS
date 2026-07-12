import { existsSync } from 'node:fs';
import path from 'node:path';

export const resolveProtoPath = (relativePath: string): string => {
  const configured = process.env.AION_PROTO_ROOT?.trim();
  const roots = [
    configured,
    path.resolve(process.cwd(), '../schemas/v1/protos'),
    path.resolve(process.cwd(), 'schemas/v1/protos'),
    '/protos',
  ].filter((value): value is string => Boolean(value));

  for (const root of roots) {
    const candidate = path.resolve(root, relativePath);
    if (existsSync(candidate)) {
      return candidate;
    }
  }
  throw new Error(`canonical protobuf source not found: ${relativePath}`);
};
