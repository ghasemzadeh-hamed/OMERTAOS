import type { NextApiRequest, NextApiResponse } from 'next';
import { bridge } from './_bridge';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { task, payload } = req.body || {};
  const result = await bridge(task, payload);
  res.status(200).json(result);
}
