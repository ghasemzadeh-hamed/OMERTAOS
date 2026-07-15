import dotenv from 'dotenv';

dotenv.config();

export type BridgeConfig = {
  gatewayUrl: string;
  adminToken: string;
  logLevel: string;
  uiOrigin?: string;
};

export function loadConfig(env = process.env): BridgeConfig {
  const gatewayUrl = env.OMERTA_GATEWAY_URL || 'http://localhost:8080';
  const adminToken = env.OMERTA_ADMIN_TOKEN || '';
  const logLevel = env.OMERTA_BRIDGE_LOG_LEVEL || 'info';
  const uiOrigin = env.BRIDGE_UI_ORIGIN;

  if (!adminToken) {
    throw new Error('OMERTA_ADMIN_TOKEN is required');
  }

  return { gatewayUrl, adminToken, logLevel, uiOrigin };
}
