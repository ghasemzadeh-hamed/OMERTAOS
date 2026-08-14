'use client';

import { ReactNode, useMemo, useState } from 'react';
import GlassPanel from '@/components/GlassPanel';

const steps = ['Language', 'Services', 'Models', 'Telemetry'] as const;

type StepIndex = 0 | 1 | 2 | 3;

type StepContent = {
  title: string;
  description: string;
  body: ReactNode;
};

export default function SetupPage() {
  const [activeStep, setActiveStep] = useState<StepIndex>(0);
  const telemetryDefault = (process.env.NEXT_PUBLIC_TELEMETRY_OPT_IN ?? 'false').toLowerCase() === 'true';
  const [telemetryOptIn, setTelemetryOptIn] = useState<boolean>(telemetryDefault);

  const stepContent = useMemo<StepContent[]>(
    () => [
      {
        title: 'Language and layout',
        description: 'Choose your preferred locale and text direction.',
        body: (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">Locale</span>
              <select className="glass-input cursor-pointer bg-white/10">
                <option value="en">English</option>
                <option value="fa">Persian</option>
              </select>
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">Text direction</span>
              <select className="glass-input cursor-pointer bg-white/10">
                <option value="ltr">LTR - Left to right</option>
                <option value="rtl">RTL - Right to left</option>
              </select>
            </label>
            <label className="space-y-2 text-left sm:col-span-2">
              <span className="text-sm text-white/75">Theme</span>
              <div className="flex flex-wrap gap-3">
                {['Dark', 'Dim', 'Light'].map((mode) => (
                  <button key={mode} type="button" className="glass-button px-6">
                    {mode}
                  </button>
                ))}
              </div>
            </label>
          </div>
        ),
      },
      {
        title: 'Core services',
        description: 'Configure connections for Postgres, Redis, and MinIO.',
        body: (
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="space-y-2 text-left sm:col-span-2">
              <span className="text-sm text-white/75">Postgres (DSN)</span>
              <input className="glass-input" placeholder="postgresql://user:pass@localhost:5432/aion" />
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">Redis</span>
              <input className="glass-input" placeholder="redis://localhost:6379/0" />
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">MinIO endpoint</span>
              <input className="glass-input" placeholder="http://localhost:9000" />
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">Bucket</span>
              <input className="glass-input" placeholder="aion-artifacts" />
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">MinIO access key</span>
              <input className="glass-input" placeholder="ACCESS_KEY" />
            </label>
            <label className="space-y-2 text-left">
              <span className="text-sm text-white/75">MinIO secret key</span>
              <input className="glass-input" placeholder="SECRET_KEY" type="password" />
            </label>
          </div>
        ),
      },
      {
        title: 'Models',
        description: 'Select model providers and defaults.',
        body: (
          <div className="space-y-4 text-left">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm text-white/75">Provider</span>
                <select className="glass-input cursor-pointer bg-white/10">
                  <option>Ollama</option>
                  <option>OpenAI</option>
                  <option>Google Gemini</option>
                </select>
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">Chat model</span>
                <input className="glass-input" placeholder="gpt-4o-mini" />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">Embedding model</span>
                <input className="glass-input" placeholder="nomic-embed-text" />
              </label>
              <label className="space-y-2">
                <span className="text-sm text-white/75">Monthly budget (USD)</span>
                <input className="glass-input" type="number" placeholder="250" />
              </label>
            </div>
            <label className="space-y-2">
              <span className="text-sm text-white/75">Notes</span>
              <textarea className="glass-input h-28 resize-none" placeholder="Additional notes" />
            </label>
          </div>
        ),
      },
      {
        title: 'Telemetry',
        description: 'Enable or disable anonymous telemetry.',
        body: (
          <div className="space-y-4 text-left">
            <div className="rounded-2xl border border-white/15 bg-white/5 p-4">
              <h3 className="text-sm font-medium text-white/80">What we collect</h3>
              <ul className="mt-3 space-y-2 text-sm text-white/70">
                <li>Health and uptime signals</li>
                <li>Error counts and crash traces</li>
                <li>Feature usage metrics</li>
              </ul>
            </div>
            <label className="flex items-center justify-between rounded-2xl border border-white/15 bg-white/5 px-4 py-3">
              <span className="text-sm text-white/75">Allow anonymous telemetry</span>
              <input
                type="checkbox"
                className="h-5 w-5 cursor-pointer accent-emerald-500"
                checked={telemetryOptIn}
                onChange={(event) => setTelemetryOptIn(event.target.checked)}
              />
            </label>
            <p className="text-xs leading-6 text-white/60">
              Controlled by <code className="rounded bg-white/10 px-1">AION_TELEMETRY_OPT_IN</code> in the environment.
            </p>
            <p className="text-sm leading-7 text-white/70">
              No API keys or user content are collected; only anonymous metrics are sent.
            </p>
          </div>
        ),
      },
    ],
    [telemetryOptIn],
  );

  const goToStep = (direction: 'prev' | 'next') => {
    setActiveStep((current) => {
      if (direction === 'prev') {
        return Math.max(0, current - 1) as StepIndex;
      }
      return Math.min(steps.length - 1, current + 1) as StepIndex;
    });
  };

  return (
    <main className="min-h-dvh p-6 text-white" dir="ltr">
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <GlassPanel className="p-4 sm:p-6">
          <header className="flex flex-col gap-2 text-left sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-white/90">Welcome to AION-OS</h1>
              <p className="text-sm text-white/65">Configure Control, Gateway, and UI with the Liquid Glass theme.</p>
            </div>
            <span className="text-sm text-white/60">Step {activeStep + 1} of {steps.length}</span>
          </header>
          <div className="mt-4 flex flex-wrap justify-start gap-2">
            {steps.map((label, index) => {
              const isActive = index === activeStep;
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => setActiveStep(index as StepIndex)}
                  className={`glass-button px-4 py-2 text-xs sm:text-sm ${isActive ? 'bg-white/25' : 'bg-white/10 hover:bg-white/15'}`}
                >
                  {index + 1}. {label}
                </button>
              );
            })}
          </div>
        </GlassPanel>

        <GlassPanel className="p-4 sm:p-6">
          <div className="space-y-2 text-left">
            <h2 className="text-xl font-semibold text-white/90">{stepContent[activeStep].title}</h2>
            <p className="text-sm text-white/70">{stepContent[activeStep].description}</p>
          </div>
          <div className="mt-4">{stepContent[activeStep].body}</div>
          <div className="mt-6 flex items-center justify-between text-sm text-white/70">
            <button
              type="button"
              onClick={() => goToStep('prev')}
              className="glass-button px-4 py-2 disabled:opacity-60"
              disabled={activeStep === 0}
            >
              Previous
            </button>
            <button
              type="button"
              onClick={() => goToStep('next')}
              className="glass-button px-4 py-2 disabled:opacity-60"
              disabled={activeStep === steps.length - 1}
            >
              Next
            </button>
          </div>
        </GlassPanel>
      </div>
    </main>
  );
}
