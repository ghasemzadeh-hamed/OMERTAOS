'use client';

import { useEffect, useMemo, useState } from 'react';

type FeatureDomain = {
  id: string;
  title: string;
  items: string[];
};

type FeatureCatalogPayload = {
  total_domains: number;
  total_feature_groups: number;
  domains: FeatureDomain[];
};

const CONTROL_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';

export default function FeatureCatalogPage() {
  const [catalog, setCatalog] = useState<FeatureCatalogPayload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setError(null);
      try {
        const res = await fetch(`${CONTROL_BASE}/api/feature-catalog`, { credentials: 'include' });
        if (!res.ok) {
          throw new Error(`Request failed: ${res.status}`);
        }
        const body = (await res.json()) as FeatureCatalogPayload;
        setCatalog(body);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      }
    };
    load();
  }, []);

  const domains = useMemo(() => catalog?.domains ?? [], [catalog]);

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-cyan-200/20 bg-gradient-to-br from-slate-900/70 via-cyan-900/20 to-indigo-900/20 p-5 shadow-2xl backdrop-blur-xl">
        <h2 className="text-2xl font-semibold text-white">OMERTAOS Feature Catalog</h2>
        <p className="mt-2 text-sm text-cyan-100/80">
          Backend-powered domain map for planning API, orchestration, and UI implementation.
        </p>
        {catalog && (
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            <span className="rounded-full border border-white/20 bg-white/10 px-3 py-1 text-white/90">
              Domains: {catalog.total_domains}
            </span>
            <span className="rounded-full border border-cyan-200/20 bg-cyan-400/10 px-3 py-1 text-cyan-100">
              Feature groups: {catalog.total_feature_groups}
            </span>
          </div>
        )}
      </header>

      {error && <p className="rounded-xl border border-rose-300/30 bg-rose-500/10 p-3 text-sm text-rose-200">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {domains.map((domain) => (
          <article
            key={domain.id}
            className="rounded-2xl border border-white/15 bg-white/5 p-4 shadow-xl backdrop-blur-xl transition hover:-translate-y-0.5 hover:bg-white/10"
          >
            <h3 className="text-base font-semibold text-white">{domain.title}</h3>
            <p className="mt-1 text-xs text-cyan-100/70">{domain.items.length} capability groups</p>
            <ul className="mt-3 space-y-2 text-sm text-white/80">
              {domain.items.map((item) => (
                <li key={item} className="rounded-lg border border-white/10 bg-black/20 px-2 py-1">
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </div>
  );
}
