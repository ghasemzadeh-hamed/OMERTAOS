'use client';

import { useEffect, useState } from 'react';

import { Button } from '@/components/ui/button';

const installCommand = 'bash scripts/claude/install-claude-code.sh';
const bootstrapCommand = 'bash scripts/claude/bootstrap-marketplace.sh';
const loginWarning = 'Login is interactive; run claude once in a trusted terminal session.';

type ClaudeStatus = {
  claude: { installed: boolean; path?: string; version?: string };
  settings: { present: boolean; valid: boolean; error?: string };
  recommendedPlugins: string[];
  marketplace?: string;
  instructions?: {
    installCommand?: string;
    bootstrapCommand?: string;
    marketplaceCommand?: string;
    pluginCommands?: string[];
    note?: string;
  };
};

type CopyButtonProps = { text: string; label: string };

function CopyButton({ text, label }: CopyButtonProps) {
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      console.error('Unable to copy', error);
    }
  };

  return (
    <Button variant="secondary" size="sm" onClick={handleCopy} className="text-sm">
      {label}
    </Button>
  );
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${
        ok ? 'bg-emerald-600/30 text-emerald-100' : 'bg-amber-600/30 text-amber-50'
      }`}
    >
      <span className={`h-2 w-2 rounded-full ${ok ? 'bg-emerald-300' : 'bg-amber-300'}`} />
      {label}
    </span>
  );
}

export default function ClaudePage() {
  const [status, setStatus] = useState<ClaudeStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/api/claude/status', { cache: 'no-store' });
        if (!res.ok) {
          setError('Unable to load Claude status');
          return;
        }
        const data = (await res.json()) as ClaudeStatus;
        setStatus(data);
      } catch (err) {
        setError('Unable to load Claude status');
      }
    };

    load();
  }, []);

  const pluginCommands =
    status?.instructions?.pluginCommands ??
    status?.recommendedPlugins?.map((plugin) => `/plugin install ${plugin}`) ?? [];

  return (
    <div className="space-y-6 text-right text-white/90">
      <header className="space-y-2">
        <h2 className="text-2xl font-semibold">Claude Code marketplace</h2>
        <p className="text-sm text-white/65">
          Install Claude Code, register the wshobson/agents marketplace, and enable curated plugins for OMERTAOS.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-left">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs uppercase tracking-wide text-white/60">Binary</p>
              <h3 className="text-lg font-semibold text-white/90">Claude Code</h3>
            </div>
            {status && (
              <StatusPill
                ok={status.claude?.installed ?? false}
                label={status.claude?.installed ? 'Installed' : 'Not installed'}
              />
            )}
          </div>
          <dl className="space-y-1 text-sm text-white/75">
            <div className="flex justify-between gap-2">
              <dt>Version</dt>
              <dd>{status?.claude?.version || 'Unknown'}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt>Path</dt>
              <dd className="truncate text-emerald-100">{status?.claude?.path || 'Not detected'}</dd>
            </div>
          </dl>
          <div className="flex flex-wrap gap-2">
            <CopyButton text={status?.instructions?.installCommand || installCommand} label="Copy install" />
            <CopyButton text="claude" label="Open TUI" />
          </div>
        </div>

        <div className="space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-left">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="text-xs uppercase tracking-wide text-white/60">Project settings</p>
              <h3 className="text-lg font-semibold text-white/90">Marketplace defaults</h3>
            </div>
            {status && (
              <StatusPill
                ok={(status.settings?.present ?? false) && (status.settings?.valid ?? false)}
                label={status.settings?.valid ? 'Valid' : 'Missing/invalid'}
              />
            )}
          </div>
          <p className="text-sm text-white/75">
            Repo-local settings live in <code className="rounded bg-black/40 px-1 py-0.5 text-xs">.claude/settings.json</code> and
            register the {status?.marketplace || 'wshobson/agents'} marketplace with recommended plugins.
          </p>
          <div className="flex flex-wrap gap-2">
            <CopyButton text={status?.instructions?.bootstrapCommand || bootstrapCommand} label="Copy bootstrap" />
            <CopyButton
              text={status?.instructions?.marketplaceCommand || '/plugin marketplace add wshobson/agents'}
              label="Copy marketplace"
            />
          </div>
          {status?.settings?.error && !status.settings.valid && (
            <p className="text-xs text-amber-200">{status.settings.error}</p>
          )}
        </div>
      </div>

      <section className="space-y-3 rounded-2xl border border-white/10 bg-black/40 p-4 text-left">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-white/90">Recommended plugins</h3>
            <p className="text-sm text-white/70">Run these commands inside Claude after logging in.</p>
          </div>
          <CopyButton text={pluginCommands.join('\n')} label="Copy all" />
        </div>
        <div className="space-y-2 text-sm text-white/80">
          {pluginCommands.map((cmd) => (
            <div
              key={cmd}
              className="flex items-center justify-between gap-2 rounded-xl border border-white/10 bg-white/5 px-3 py-2"
            >
              <span className="truncate font-mono text-xs text-emerald-100">{cmd}</span>
              <CopyButton text={cmd} label="Copy" />
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-2xl border border-amber-400/40 bg-amber-500/10 p-4 text-left text-amber-100">
        <h3 className="text-sm font-semibold">Interactive login required</h3>
        <p className="text-xs text-amber-50">{status?.instructions?.note || loginWarning}</p>
      </section>

      {error && <p className="text-sm text-red-300">{error}</p>}
    </div>
  );
}
