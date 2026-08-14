import type { NextApiRequest, NextApiResponse } from 'next';

import { GATEWAY_HTTP_URL } from '@/lib/gatewayConfig';

export async function bridge(task: string, payload: unknown) {
  const response = await fetch(`${GATEWAY_HTTP_URL}/task`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ task, payload }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`bridge ${task} failed: ${text}`);
  }
  return response.json();
}

export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  res.status(404).json({ error: 'not-implemented' });
}
