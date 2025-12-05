import axios, { AxiosInstance } from 'axios';
import { Logger } from './logger.js';
import { BridgeConfig } from './config.js';

export class OmertaClient {
  private gateway: AxiosInstance;
  private control: AxiosInstance;

  constructor(private config: BridgeConfig, private logger = new Logger(config.logLevel as any)) {
    const authHeader = { Authorization: `Bearer ${config.adminToken}` };
    this.gateway = axios.create({
      baseURL: config.gatewayUrl,
      headers: authHeader,
      timeout: 10_000,
    });
    this.control = axios.create({
      baseURL: config.controlUrl,
      headers: authHeader,
      timeout: 10_000,
    });
  }

  async getHealth() {
    this.logger.debug('calling gateway health');
    const [gateway, control] = await Promise.all([
      this.gateway.get('/health').then((r) => r.data),
      this.control.get('/health').then((r) => r.data),
    ]);
    return { gateway, control };
  }

  async listAgents() {
    const res = await this.gateway.get('/agents');
    return res.data;
  }

  async getAgent(agentId: string) {
    const res = await this.gateway.get(`/agents/${agentId}`);
    return res.data;
  }

  async runTask(agentId: string, intent: string, params: Record<string, unknown>) {
    const res = await this.gateway.post('/tasks', { agentId, intent, params });
    return res.data;
  }

  async getTaskStatus(taskId: string) {
    const res = await this.gateway.get(`/tasks/${taskId}`);
    return res.data;
  }
}
