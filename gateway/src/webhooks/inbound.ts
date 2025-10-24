import crypto from 'node:crypto';
import type { FastifyInstance } from 'fastify';
import { gatewayConfig } from '../config.js';
import { authPreHandler } from '../auth/index.js';
import { orchestrateCommand } from '../chatops/dispatcher.js';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import yaml from 'yaml';

let allowlist: string[] = [];
try {
  const policyPath = resolve(process.cwd(), 'policies/webhooks.yaml');
  const content = readFileSync(policyPath, 'utf8');
  const parsed = yaml.parse(content);
  allowlist = (parsed?.inbound?.allowlist ?? []).map((value: string) => String(value).trim());
} catch (error) {
  allowlist = [];
}

const verifySignature = (rawBody: string, signature: string | undefined) => {
  if (!gatewayConfig.inboundWebhookSecret) {
    throw new Error('Inbound webhook secret not configured');
  }
  if (!signature) {
    return false;
  }
  const expected = crypto.createHmac('sha256', gatewayConfig.inboundWebhookSecret).update(rawBody).digest('hex');
  const left = Buffer.from(expected, 'utf8');
  const right = Buffer.from(signature, 'utf8');
  if (left.length !== right.length) {
    return false;
  }
  return crypto.timingSafeEqual(left, right);
};

export const registerInboundWebhook = (app: FastifyInstance) => {
  app.post('/v1/webhooks/inbound', {
    preHandler: authPreHandler(['admin']),
  }, async (request, reply) => {
    const payload = typeof request.body === 'object' && request.body ? request.body : {};
    const serialized = JSON.stringify(payload);
    const valid = verifySignature(serialized, request.headers['x-aion-signature']?.toString());
    if (!valid) {
      throw reply.forbidden('Invalid webhook signature');
    }
    const command = payload['command'];
    if (typeof command !== 'string') {
      throw reply.badRequest('command is required');
    }
    const normalized = command.startsWith('/') ? command.slice(1) : command;
    const verb = normalized.split(' ')[0];
    if (!allowlist.includes(normalized) && !allowlist.includes(verb)) {
      throw reply.forbidden('Command not allowlisted');
    }
    const result = await orchestrateCommand(command, {
      actor: 'webhook',
      tenant: request.headers['x-tenant']?.toString(),
    });
    return { status: 'accepted', result };
  });
};
