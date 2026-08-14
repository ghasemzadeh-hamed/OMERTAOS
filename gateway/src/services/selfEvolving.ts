import type { FastifyBaseLogger } from 'fastify';

import { gatewayConfig } from '../config.js';

const DEFAULT_TIMEOUT_MS = 1_500;

const fetchWithTimeout = async (url: string, init: RequestInit = {}, timeoutMs = DEFAULT_TIMEOUT_MS) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
};

export const resolveModelForAgent = async (
  agentId: string,
  defaultModel: string,
  logger: FastifyBaseLogger,
): Promise<string> => {
  if (!gatewayConfig.selfEvolving.enabled) {
    return defaultModel;
  }
  const registryUrl = gatewayConfig.selfEvolving.modelRegistryUrl;
  if (!registryUrl) {
    return defaultModel;
  }

  try {
    const response = await fetchWithTimeout(`${registryUrl}/routes/${encodeURIComponent(agentId)}`, {
      method: 'GET',
      headers: { accept: 'application/json' },
    });
    if (!response.ok) {
      if (response.status !== 404) {
        const body = await response.text();
        logger.warn(
          { status: response.status, agentId, body },
          'Self-evolving registry lookup failed; falling back to default model',
        );
      }
      return defaultModel;
    }

    const data = (await response.json()) as { model_name?: string };
    const modelName = typeof data?.model_name === 'string' ? data.model_name.trim() : '';
    return modelName || defaultModel;
  } catch (error) {
    logger.warn({ err: error, agentId }, 'Failed to resolve model route for agent');
    return defaultModel;
  }
};

interface InteractionPayload {
  agentId: string;
  userId?: string;
  modelVersion: string;
  inputText: string;
  outputText: string;
  channel?: string;
}

export const logInteraction = async (
  payload: InteractionPayload,
  logger: FastifyBaseLogger,
): Promise<void> => {
  if (!gatewayConfig.selfEvolving.enabled) {
    return;
  }
  const memoryUrl = gatewayConfig.selfEvolving.memoryUrl;
  if (!memoryUrl) {
    return;
  }

  try {
    const response = await fetchWithTimeout(
      `${memoryUrl}/interactions`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          agent_id: payload.agentId,
          user_id: payload.userId,
          model_version: payload.modelVersion,
          input_text: payload.inputText,
          output_text: payload.outputText,
          channel: payload.channel ?? gatewayConfig.selfEvolving.defaultChannel,
        }),
      },
      DEFAULT_TIMEOUT_MS,
    );

    if (!response.ok) {
      const body = await response.text();
      logger.warn(
        { status: response.status, agentId: payload.agentId, body },
        'Failed to persist interaction in memory service',
      );
    }
  } catch (error) {
    logger.warn({ err: error, agentId: payload.agentId }, 'Error sending interaction to memory service');
  }
};
