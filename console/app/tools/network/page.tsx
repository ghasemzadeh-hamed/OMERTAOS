'use client';

import { validateProxyForm, type ProxyFormState, type ProxyProfile } from "@/lib/network/proxyValidation";
import { CheckCircle2, FlaskConical, Pencil, Plus, ShieldCheck, Trash2 } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';

const GATEWAY_BASE = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:3000';

const PROXY_TYPES = ['direct', 'http', 'socks5', 'vless'] as const;
const SCOPES = ['global', 'ai_providers', 'model_registry', 'agent_runtime', 'custom_domains'] as const;
const SECRET_FIELDS = ['uuid', 'password', 'private_key', 'public_key', 'short_id'] as const;

type ProxyType = (typeof PROXY_TYPES)[number];
type ProxyScope = (typeof SCOPES)[number];
type SecretField = (typeof SECRET_FIELDS)[number];

const emptyForm: ProxyFormState = {
  name: '',
  type: 'direct',
  enabled: false,
  scope: 'global',
  host: '',
  port: '',
  transport: '',
  security: '',
  sni: '',
  flow: '',
  path: '',
  fallback_direct: false,
  health_check_url: '',
  secrets: {
    uuid: '',
    password: '',
    private_key: '',
    public_key: '',
    short_id: '',
  },
};
const formFromProfile = (profile: ProxyProfile): ProxyFormState => ({
  ...emptyForm,
  name: profile.name,
  type: profile.type,
  enabled: profile.enabled,
  scope: profile.scope,
  host: profile.host ?? '',
  port: profile.port ? String(profile.port) : '',
  transport: profile.transport ?? '',
  security: profile.security ?? '',
  sni: profile.sni ?? '',
  flow: profile.flow ?? '',
  path: profile.path ?? '',
  fallback_direct: profile.fallback_direct,
  health_check_url: profile.health_check_url ?? '',
  secrets: { ...emptyForm.secrets },
});

const payloadFromForm = (form: ProxyFormState, editing: boolean) => {
  const secrets = Object.fromEntries(
    Object.entries(form.secrets).filter(([, value]) => value.trim().length > 0),
  );
  return {
    name: form.name.trim(),
    type: form.type,
    enabled: form.enabled,
    scope: form.scope,
    host: form.type === 'direct' ? null : form.host.trim(),
    port: form.type === 'direct' ? null : Number(form.port),
    transport: form.transport.trim() || null,
    security: form.security.trim() || null,
    sni: form.sni.trim() || null,
    flow: form.flow.trim() || null,
    path: form.path.trim() || null,
    fallback_direct: form.fallback_direct,
    health_check_url: form.health_check_url.trim() || null,
    ...(Object.keys(secrets).length > 0 ? { secrets } : editing ? {} : { secrets: {} }),
  };
};

async function gatewayRequest(path: string, init?: RequestInit) {
  const response = await fetch(`${GATEWAY_BASE}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  if (response.status === 204) {
    return {};
  }
  return response.json();
}

export default function NetworkConfigPage() {
  const [profiles, setProfiles] = useState<ProxyProfile[]>([]);
  const [form, setForm] = useState<ProxyFormState>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);

  const editingProfile = useMemo(
    () => profiles.find((profile) => profile.id === editingId) ?? null,
    [profiles, editingId],
  );

  const load = async () => {
    const data = await gatewayRequest('/v1/network/proxies');
    setProfiles(data.items ?? []);
  };

  useEffect(() => {
    load().catch((error) => setStatus(`Failed to load proxy profiles: ${error.message}`));
  }, []);

  const update = (patch: Partial<ProxyFormState>) => {
    setForm((current) => ({ ...current, ...patch }));
  };

  const updateSecret = (field: SecretField, value: string) => {
    setForm((current) => ({
      ...current,
      secrets: { ...current.secrets, [field]: value },
    }));
  };

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const submit = async () => {
    const validation = validateProxyForm(form, Boolean(editingProfile?.has_secrets));
    if (validation) {
      setStatus(validation);
      return;
    }
    setStatus(null);
    const path = editingId ? `/v1/network/proxies/${editingId}` : '/v1/network/proxies';
    await gatewayRequest(path, {
      method: editingId ? 'PUT' : 'POST',
      body: JSON.stringify(payloadFromForm(form, Boolean(editingId))),
    });
    await load();
    resetForm();
    setStatus(editingId ? 'Proxy profile updated' : 'Proxy profile created');
  };

  const runProfileAction = async (profile: ProxyProfile, action: 'enable' | 'disable' | 'test' | 'set-default') => {
    setBusyId(profile.id);
    setStatus(null);
    try {
      const result = await gatewayRequest(`/v1/network/proxies/${profile.id}/${action}`, {
        method: 'POST',
        body: JSON.stringify({}),
      });
      await load();
      setStatus(action === 'test' ? `Test ${result.ok ? 'passed' : 'failed'} via ${result.routed_via}` : 'Proxy profile updated');
    } catch (error) {
      setStatus(`Action failed: ${(error as Error).message}`);
    } finally {
      setBusyId(null);
    }
  };

  const remove = async (profile: ProxyProfile) => {
    setBusyId(profile.id);
    try {
      await gatewayRequest(`/v1/network/proxies/${profile.id}`, { method: 'DELETE' });
      await load();
      if (editingId === profile.id) {
        resetForm();
      }
      setStatus('Proxy profile deleted');
    } catch (error) {
      setStatus(`Delete failed: ${(error as Error).message}`);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="space-y-6 text-right">
      <header className="space-y-1">
        <h2 className="text-2xl font-semibold text-white/90">Network Proxy Manager</h2>
        <p className="text-xs text-white/60">Configure outbound routes for external providers through the Gateway and Control Plane.</p>
      </header>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_24rem]">
        <div className="space-y-3">
          {profiles.length === 0 ? (
            <div className="rounded-md border border-white/10 bg-white/5 p-4 text-sm text-white/60">No proxy profiles configured.</div>
          ) : (
            profiles.map((profile) => (
              <div key={profile.id} className="rounded-md border border-white/10 bg-white/5 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="space-y-2 text-left">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-base font-semibold text-white">{profile.name}</span>
                      <span className="rounded bg-white/10 px-2 py-1 text-xs uppercase tracking-normal text-white/70">{profile.type}</span>
                      <span className="rounded bg-cyan-500/15 px-2 py-1 text-xs text-cyan-100">{profile.scope}</span>
                      {profile.is_default && (
                        <span className="inline-flex items-center gap-1 rounded bg-emerald-500/15 px-2 py-1 text-xs text-emerald-100">
                          <CheckCircle2 className="h-3.5 w-3.5" /> default
                        </span>
                      )}
                      {profile.has_secrets && (
                        <span className="inline-flex items-center gap-1 rounded bg-white/10 px-2 py-1 text-xs text-white/70">
                          <ShieldCheck className="h-3.5 w-3.5" /> secrets masked
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-white/60">
                      {profile.type === 'direct' ? 'Direct outbound access' : `${profile.host}:${profile.port}`}
                      {profile.health_check_url ? ` / health ${profile.health_check_url}` : ''}
                    </div>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Switch
                      aria-label={`${profile.enabled ? 'Disable' : 'Enable'} ${profile.name}`}
                      checked={profile.enabled}
                      disabled={busyId === profile.id}
                      onCheckedChange={() => runProfileAction(profile, profile.enabled ? 'disable' : 'enable')}
                    />
                    <Button type="button" variant="outline" size="icon" title="Test connection" disabled={busyId === profile.id} onClick={() => runProfileAction(profile, 'test')}>
                      <FlaskConical className="h-4 w-4" />
                    </Button>
                    <Button type="button" variant="outline" size="icon" title="Set default" disabled={busyId === profile.id} onClick={() => runProfileAction(profile, 'set-default')}>
                      <CheckCircle2 className="h-4 w-4" />
                    </Button>
                    <Button type="button" variant="outline" size="icon" title="Edit profile" onClick={() => { setEditingId(profile.id); setForm(formFromProfile(profile)); }}>
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button type="button" variant="destructive" size="icon" title="Delete profile" disabled={busyId === profile.id} onClick={() => remove(profile)}>
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        <form className="space-y-4 rounded-md border border-white/10 bg-white/5 p-4 text-left" onSubmit={(event) => { event.preventDefault(); void submit(); }}>
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white">{editingProfile ? 'Edit proxy profile' : 'Create proxy profile'}</h3>
            <Button type="button" variant="ghost" size="sm" onClick={resetForm}>
              <Plus className="mr-2 h-4 w-4" /> New
            </Button>
          </div>

          <label className="block space-y-1 text-xs text-white/60">
            <span>Name</span>
            <Input aria-label="Proxy profile name" value={form.name} onChange={(event) => update({ name: event.target.value })} />
          </label>

          <div className="grid gap-3 sm:grid-cols-2">
            <label className="block space-y-1 text-xs text-white/60">
              <span>Type</span>
              <select aria-label="Proxy type" value={form.type} onChange={(event) => update({ type: event.target.value as ProxyType })} className="h-10 w-full rounded-md border border-white/20 bg-slate-950 px-3 text-sm text-white">
                {PROXY_TYPES.map((type) => <option key={type} value={type}>{type}</option>)}
              </select>
            </label>
            <label className="block space-y-1 text-xs text-white/60">
              <span>Scope</span>
              <select aria-label="Proxy scope" value={form.scope} onChange={(event) => update({ scope: event.target.value as ProxyScope })} className="h-10 w-full rounded-md border border-white/20 bg-slate-950 px-3 text-sm text-white">
                {SCOPES.map((scope) => <option key={scope} value={scope}>{scope}</option>)}
              </select>
            </label>
          </div>

          <div className="grid gap-3 sm:grid-cols-[1fr_7rem]">
            <label className="block space-y-1 text-xs text-white/60">
              <span>Host</span>
              <Input aria-label="Proxy host" value={form.host} disabled={form.type === 'direct'} onChange={(event) => update({ host: event.target.value })} />
            </label>
            <label className="block space-y-1 text-xs text-white/60">
              <span>Port</span>
              <Input aria-label="Proxy port" inputMode="numeric" value={form.port} disabled={form.type === 'direct'} onChange={(event) => update({ port: event.target.value })} />
            </label>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <Input aria-label="Transport" placeholder="transport" value={form.transport} onChange={(event) => update({ transport: event.target.value })} />
            <Input aria-label="Security" placeholder="security" value={form.security} onChange={(event) => update({ security: event.target.value })} />
            <Input aria-label="SNI" placeholder="sni" value={form.sni} onChange={(event) => update({ sni: event.target.value })} />
            <Input aria-label="Flow" placeholder="flow" value={form.flow} onChange={(event) => update({ flow: event.target.value })} />
          </div>

          <Input aria-label="Path" placeholder="path" value={form.path} onChange={(event) => update({ path: event.target.value })} />
          <Input aria-label="Health check URL" placeholder="https://api.openai.com/v1/models" value={form.health_check_url} onChange={(event) => update({ health_check_url: event.target.value })} />

          <div className="grid gap-3 sm:grid-cols-2">
            {SECRET_FIELDS.map((field) => (
              <label key={field} className="block space-y-1 text-xs text-white/60">
                <span>{field}</span>
                <Input
                  aria-label={`Secret ${field}`}
                  type="password"
                  autoComplete="new-password"
                  placeholder={editingProfile?.has_secrets ? '********' : ''}
                  value={form.secrets[field]}
                  onChange={(event) => updateSecret(field, event.target.value)}
                />
              </label>
            ))}
          </div>

          <div className="flex items-center justify-between rounded-md border border-white/10 px-3 py-2 text-sm text-white/70">
            <span>Fallback direct</span>
            <Switch checked={form.fallback_direct} onCheckedChange={(checked) => update({ fallback_direct: checked })} />
          </div>
          <div className="flex items-center justify-between rounded-md border border-white/10 px-3 py-2 text-sm text-white/70">
            <span>Enabled</span>
            <Switch checked={form.enabled} onCheckedChange={(checked) => update({ enabled: checked })} />
          </div>

          <Button type="submit" className="w-full">
            {editingProfile ? 'Save proxy profile' : 'Create proxy profile'}
          </Button>
        </form>
      </section>

      {status && <div className="rounded-md border border-white/10 bg-white/5 p-3 text-xs text-white/70">{status}</div>}
    </div>
  );
}





