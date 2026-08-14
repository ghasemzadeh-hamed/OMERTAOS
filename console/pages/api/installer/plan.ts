import type { NextApiRequest, NextApiResponse } from 'next';
import { bridge } from './_bridge';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const plan = await bridge('plan.partition', req.body || {});
  res.status(200).json(plan);
}
