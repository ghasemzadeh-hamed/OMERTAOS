import type { NextApiRequest, NextApiResponse } from 'next';
import { bridge } from './_bridge';

export default async function handler(_req: NextApiRequest, res: NextApiResponse) {
  const hw = await bridge('probe.hw', {});
  res.status(200).json(hw);
}
