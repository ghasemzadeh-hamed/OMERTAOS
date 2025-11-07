import type { NextApiRequest, NextApiResponse } from 'next';
import { bridge } from './_bridge';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const data = await bridge('profiles.list', {});
    return res.status(200).json(data);
  }
  if (req.method === 'POST') {
    const data = await bridge('profiles.apply', req.body);
    return res.status(200).json(data);
  }
  res.status(405).end();
}
