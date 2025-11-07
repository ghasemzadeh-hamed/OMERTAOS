'use client';

import { useEffect, useState } from 'react';

const CONTROL_BASE = process.env.NEXT_PUBLIC_CONTROL_BASE || 'http://localhost:8000';

type ConfigState = {
  modelDirectories: string;
  defaultModel: string;
  qdrantUrl: string;
  minioEndpoint: string;
  minioAccessKey: string;
  minioSecretKey: string;
  postgresDsn: string;
  mongoDsn: string;
  tenancyMode: string;
  profile: string;
  metricsEnabled: string;
  metricsPromUrl: string;
};

const initialState: ConfigState = {
  modelDirectories: '',
  defaultModel: '',
  qdrantUrl: '',
  minioEndpoint: '',
  minioAccessKey: '',
  minioSecretKey: '',
  postgresDsn: '',
  mongoDsn: '',
  tenancyMode: '',
  profile: '',
  metricsEnabled: '',
  metricsPromUrl: '',
};

export default function ConfigCenterPage() {
  const [form, setForm] = useState<ConfigState>(initialState);
  const [effective, setEffective] = useState<any>({});
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      const res = await fetch(`${CONTROL_BASE}/api/config`, { credentials: 'include' });
      if (!res.ok) {
        setStatus('Failed to load configuration');
        return;
      }
      const data = await res.json();
      const file = data.file || {};
      setEffective(data.effective || {});
      setForm({
        modelDirectories: (file.model?.directories ?? []).join(','),
        defaultModel: file.model?.default_model ?? '',
        qdrantUrl: file.vector_store?.qdrant_url ?? '',
        minioEndpoint: file.storage?.minio_endpoint ?? '',
        minioAccessKey: file.storage?.minio_access_key ?? '',
        minioSecretKey: file.storage?.minio_secret_key ?? '',
        postgresDsn: file.storage?.postgres_dsn ?? '',
        mongoDsn: file.vector_store?.mongo_dsn ?? '',
        tenancyMode: file.TENANCY_MODE ?? '',
        profile: file.AION_PROFILE ?? '',
        metricsEnabled: file.AION_METRICS_ENABLED ?? '',
        metricsPromUrl: file.AION_METRICS_PROM_URL ?? '',
      });
    };
    load();
  }, []);

  const updateField = (key: keyof ConfigState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const save = async () => {
    setStatus('');
    const payload: any = {
      model: {
        directories: form.modelDirectories ? form.modelDirectories.split(',').map((item) => item.trim()).filter(Boolean) : [],
        default_model: form.defaultModel || undefined,
      },
      vector_store: {
        qdrant_url: form.qdrantUrl || undefined,
        mongo_dsn: form.mongoDsn || undefined,
      },
      storage: {
        minio_endpoint: form.minioEndpoint || undefined,
        minio_access_key: form.minioAccessKey || undefined,
        minio_secret_key: form.minioSecretKey || undefined,
        postgres_dsn: form.postgresDsn || undefined,
      },
      TENANCY_MODE: form.tenancyMode || undefined,
      AION_PROFILE: form.profile || undefined,
      AION_METRICS_ENABLED: form.metricsEnabled || undefined,
      AION_METRICS_PROM_URL: form.metricsPromUrl || undefined,
    };
    const res = await fetch(`${CONTROL_BASE}/api/config`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      setStatus(`Failed to save: ${await res.text()}`);
      return;
    }
    const data = await res.json();
    setStatus('Configuration updated');
    setEffective(data.effective || {});
  };

  return (
    <div className="space-y-5 text-right">
      <header>
        <h2 className="text-2xl font-semibold text-white/90">Config Center</h2>
        <p className="text-xs text-white/60">Manage paths, databases, storage endpoints, and profile parameters.</p>
      </header>
      <div className="grid gap-4 lg:grid-cols-2">
        <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
          <h3 className="text-lg font-semibold text-white/85">Model &amp; Storage</h3>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Model directories (comma separated)</span>
            <input
              value={form.modelDirectories}
              onChange={(event) => updateField('modelDirectories', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Default model</span>
            <input
              value={form.defaultModel}
              onChange={(event) => updateField('defaultModel', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Qdrant URL</span>
            <input
              value={form.qdrantUrl}
              onChange={(event) => updateField('qdrantUrl', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Mongo DSN</span>
            <input
              value={form.mongoDsn}
              onChange={(event) => updateField('mongoDsn', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">MinIO endpoint</span>
            <input
              value={form.minioEndpoint}
              onChange={(event) => updateField('minioEndpoint', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <div className="grid gap-2 md:grid-cols-2">
            <label className="block space-y-1">
              <span className="text-xs text-white/60">MinIO access key</span>
              <input
                value={form.minioAccessKey}
                onChange={(event) => updateField('minioAccessKey', event.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
              />
            </label>
            <label className="block space-y-1">
              <span className="text-xs text-white/60">MinIO secret key</span>
              <input
                value={form.minioSecretKey}
                onChange={(event) => updateField('minioSecretKey', event.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
              />
            </label>
          </div>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Postgres DSN</span>
            <input
              value={form.postgresDsn}
              onChange={(event) => updateField('postgresDsn', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
        </section>
        <section className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
          <h3 className="text-lg font-semibold text-white/85">Tenancy &amp; Metrics</h3>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Tenancy mode</span>
            <input
              value={form.tenancyMode}
              onChange={(event) => updateField('tenancyMode', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <label className="block space-y-1">
            <span className="text-xs text-white/60">Profile</span>
            <input
              value={form.profile}
              onChange={(event) => updateField('profile', event.target.value)}
              className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            />
          </label>
          <div className="grid gap-2 md:grid-cols-2">
            <label className="block space-y-1">
              <span className="text-xs text-white/60">Metrics enabled</span>
              <input
                value={form.metricsEnabled}
                onChange={(event) => updateField('metricsEnabled', event.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
              />
            </label>
            <label className="block space-y-1">
              <span className="text-xs text-white/60">Prometheus URL</span>
              <input
                value={form.metricsPromUrl}
                onChange={(event) => updateField('metricsPromUrl', event.target.value)}
                className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2"
              />
            </label>
          </div>
          <button onClick={save} className="rounded-xl bg-emerald-500/80 px-4 py-2 text-sm text-white hover:bg-emerald-500" type="button">
            Save changes
          </button>
          {status && <div className="text-xs text-white/60">{status}</div>}
        </section>
      </div>
      <section className="rounded-2xl border border-white/10 bg-black/40 p-4 text-xs text-emerald-100">
        <h3 className="mb-2 text-sm font-semibold text-white/80">Effective configuration</h3>
        <pre className="max-h-[320px] overflow-auto">{JSON.stringify(effective, null, 2)}</pre>
      </section>
    </div>
  );
}
