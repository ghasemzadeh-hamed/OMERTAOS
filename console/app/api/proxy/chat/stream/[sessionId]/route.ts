import { NextRequest } from 'next/server';
import { createSseProxyResponse } from '../../../../../../lib/api';

export async function GET(_: NextRequest, { params }: { params: { sessionId: string } }) {
  return createSseProxyResponse(`/v1/chat/stream/${params.sessionId}`);
}
