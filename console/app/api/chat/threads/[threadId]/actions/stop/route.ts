import { NextResponse } from 'next/server';

import { stopThread } from '@/lib/osChatStore';

export function POST() {
  const result = stopThread();
  return NextResponse.json(result);
}
