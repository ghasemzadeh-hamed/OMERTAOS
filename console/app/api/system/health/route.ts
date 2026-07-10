import { NextResponse } from 'next/server';

import { resolveGatewayBase } from '@/lib/gatewayClient';

type ServiceStatus = 'ok' | 'degraded';

type ServiceCheck = {
  status: ServiceStatus;
  details: string;
};

const stripTrailingSlash = (value: string) => value.replace(/\/+$/, '');

const controlBase = () =>
  stripTrailingSlash(
    process.env.CONTROL_URL ||
      process.env.AION_CONTROL_URL ||
      process.env.AION_CONTROL_BASE_URL ||
      process.env.AION_CONTROL_BASE ||
      'http://control:8000',
  );

const gatewayBase = () =>
  stripTrailingSlash(
    process.env.GATEWAY_URL ||
      process.env.AION_GATEWAY_URL ||
      resolveGatewayBase() ||
      'http://gateway:8080',
  );

const consoleBase = () =>
  stripTrailingSlash(
    process.env.INTERNAL_CONSOLE_URL ||
      process.env.CONSOLE_URL ||
      process.env.NEXTAUTH_URL ||
      'http://localhost:3000',
  );

async function check(baseUrl: string, paths: string[] = ['/healthz', '/health']): Promise<ServiceCheck> {
  const attempts: string[] = [];

  for (const path of paths) {
    const url = `${baseUrl}${path}`;
    attempts.push(url);

    try {
      const res = await fetch(url, { cache: 'no-store' });

      if (res.ok) {
        return { status: 'ok', details: `HTTP ${res.status} ${path}` };
      }

      attempts.push(`HTTP ${res.status}`);
    } catch {
      attempts.push('unreachable');
    }
  }

  return {
    status: 'degraded',
    details: `unreachable: ${attempts.join(' | ')}`,
  };
}

export async function GET() {
  const [gateway, control, consoleSvc] = await Promise.all([
    check(gatewayBase()),
    check(controlBase()),
    check(consoleBase()),
  ]);

  const status: ServiceStatus = [gateway, control].some((service) => service.status === 'degraded')
    ? 'degraded'
    : 'ok';

  return NextResponse.json({
    status,
    services: {
      gateway,
      control,
      console: consoleSvc,
    },
    updatedAt: new Date().toISOString(),
  });
}
