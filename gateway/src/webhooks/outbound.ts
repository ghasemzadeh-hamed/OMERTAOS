import crypto from 'node:crypto';
import { gatewayConfig } from '../config.js';

type OutboundPayload = Record<string, unknown>;

type Topic = string;

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const deliverEvent = async (topic: Topic, payload: OutboundPayload) => {
  const events = gatewayConfig.outboundWebhooks.filter((hook) => hook.topics.includes(topic) || hook.topics.includes('*'));
  const body = JSON.stringify({ topic, payload, timestamp: new Date().toISOString() });
  await Promise.all(
    events.map(async (hook) => {
      let attempt = 0;
      let lastError: Error | undefined;
      while (attempt <= hook.maxRetries) {
        try {
          const signature = crypto.createHmac('sha256', hook.secret).update(body).digest('hex');
          const response = await fetch(hook.url, {
            method: 'POST',
            headers: {
              'content-type': 'application/json',
              'x-aion-topic': topic,
              'x-aion-signature': signature,
            },
            body,
          });
          if (response.ok) {
            return;
          }
          lastError = new Error(`Webhook responded with ${response.status}`);
        } catch (error) {
          lastError = error as Error;
        }
        attempt += 1;
        await delay(hook.backoffSeconds * 1000 * attempt);
      }
      if (lastError) {
        throw lastError;
      }
    })
  );
};
