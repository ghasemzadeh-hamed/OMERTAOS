import { NextResponse } from 'next/server';

import { getDatabaseDiagnostics } from '@/lib/databaseInfo';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';

const isDockerEnv = process.env.AION_DOCKER === '1' || process.env.DOCKER === 'true';
const isProdEnv = process.env.NODE_ENV === 'production';

export async function GET() {
  const diagnostics = getDatabaseDiagnostics(process.env.DATABASE_URL, isDockerEnv || isProdEnv);

  return NextResponse.json({
    provider: diagnostics.provider,
    enforced: diagnostics.enforced,
    url: diagnostics.redactedUrl,
    timestamp: new Date().toISOString(),
  });
}
