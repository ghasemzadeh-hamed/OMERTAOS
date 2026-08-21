'use client';

import Link from 'next/link';
import { useCallback, useEffect, useState } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

import { Button } from '@/components/ui/button';

type RemoteItem = Record<string, unknown>;

type RemoteCollectionPageProps = {
  endpoint: string;
  title: string;
  description: string;
  collectionKeys: string[];
  emptyLabel: string;
  itemHrefBase?: string;
};

function itemText(item: RemoteItem, keys: string[], fallback: string) {
  for (const key of keys) {
    const value = item[key];
    if (typeof value === 'string' && value.trim()) return value;
  }
  return fallback;
}

function readCollection(payload: unknown, keys: string[]) {
  if (Array.isArray(payload)) return payload.filter((item): item is RemoteItem => Boolean(item) && typeof item === 'object');
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    const value = (payload as RemoteItem)[key];
    if (Array.isArray(value)) return value.filter((item): item is RemoteItem => Boolean(item) && typeof item === 'object');
  }
  return [];
}

export default function RemoteCollectionPage({ endpoint, title, description, collectionKeys, emptyLabel, itemHrefBase }: RemoteCollectionPageProps) {
  const [items, setItems] = useState<RemoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(endpoint, { cache: 'no-store' });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const message = payload && typeof payload === 'object' && typeof (payload as RemoteItem).error === 'string'
          ? String((payload as RemoteItem).error)
          : `Request failed with HTTP ${response.status}`;
        throw new Error(message);
      }
      setItems(readCollection(payload, collectionKeys));
    } catch (loadError) {
      setItems([]);
      setError(loadError instanceof Error ? loadError.message : 'Unable to load data');
    } finally {
      setLoading(false);
    }
  }, [collectionKeys, endpoint]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <main className="min-h-dvh bg-slate-950 px-4 py-8 text-white">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="flex flex-wrap items-start justify-between gap-4 border-b border-white/10 pb-5">
          <div>
            <h1 className="text-2xl font-semibold">{title}</h1>
            <p className="mt-1 text-sm text-white/60">{description}</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => void load()} disabled={loading}>
              <RefreshCcw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button asChild variant="secondary"><Link href="/console">Console</Link></Button>
          </div>
        </header>

        {error ? (
          <section className="flex items-start gap-3 border border-amber-400/30 bg-amber-400/10 p-4">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
            <div>
              <h2 className="font-medium">Backend capability unavailable</h2>
              <p className="mt-1 text-sm text-white/65">{error}</p>
            </div>
          </section>
        ) : null}

        {!error && !loading && items.length === 0 ? (
          <p className="border border-dashed border-white/15 p-6 text-sm text-white/60">{emptyLabel}</p>
        ) : null}

        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {items.map((item, index) => {
            const id = itemText(item, ['id', 'slug', 'key'], String(index));
            const titleText = itemText(item, ['name', 'title', 'label'], id);
            const descriptionText = itemText(item, ['description', 'summary', 'status'], 'No additional details');
            const content = <><h2 className="font-medium">{titleText}</h2><p className="mt-1 line-clamp-3 text-sm leading-6 text-white/60">{descriptionText}</p></>;
            return itemHrefBase ? (
              <Link key={id} href={`${itemHrefBase}/${encodeURIComponent(id)}`} className="border border-white/10 bg-white/5 p-4 hover:bg-white/10">{content}</Link>
            ) : (
              <article key={id} className="border border-white/10 bg-white/5 p-4">{content}</article>
            );
          })}
        </section>
      </div>
    </main>
  );
}
