import Link from 'next/link';

type ServiceStatus = 'ok' | 'degraded' | 'error' | 'unknown';

type HealthResponse = {
  status?: ServiceStatus;
  setupComplete?: boolean;
  services?: Record<string, { status: ServiceStatus; details: string }>;
};

async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch('/api/dashboard/health', { cache: 'no-store' });
    if (!res.ok) {
      return null;
    }
    return res.json();
  } catch (error) {
    console.error('[console] dashboard health fetch failed', error);
    return null;
  }
}

export default async function DashboardHealthPage() {
  const health = await fetchHealth();

  return (
    <div className="p-6 space-y-4 text-white">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">System health</h1>
          <p className="text-sm text-white/70">Overview of your local AION-OS stack.</p>
        </div>
        <Link href="/" className="text-sm text-white/80 hover:text-white">Back</Link>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {health?.services
          ? Object.entries(health.services).map(([name, svc]) => (
              <div key={name} className="rounded-xl bg-white/10 p-4 border border-white/10">
                <div className="flex items-center justify-between">
                  <span className="font-medium capitalize">{name}</span>
                  <span
                    className={
                      svc.status === 'ok'
                        ? 'text-emerald-300'
                        : svc.status === 'degraded'
                          ? 'text-amber-200'
                          : 'text-rose-300'
                    }
                  >
                    {svc.status}
                  </span>
                </div>
                <p className="text-sm text-white/70 mt-2">{svc.details}</p>
              </div>
            ))
          : (
              <div className="text-sm text-white/70">Unable to load health information.</div>
            )}
      </div>
      <div className="text-sm text-white/70">
        Setup complete: {health?.setupComplete ? 'yes' : 'no'}  Overall status: {health?.status ?? 'unknown'}
      </div>
    </div>
  );
}
