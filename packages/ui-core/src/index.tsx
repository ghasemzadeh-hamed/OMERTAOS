'use client';

import React, { ComponentType, useMemo, useState } from 'react';

export interface WizardStep {
  id: string;
  title: string;
  component: ComponentType;
}

const steps: WizardStep[] = [];

export function registerSteps(nextSteps: WizardStep[]) {
  steps.splice(0, steps.length, ...nextSteps);
}

export function WizardRouter() {
  const registeredSteps = useMemo(() => steps, []);
  const [index, setIndex] = useState(0);
  const step = registeredSteps[index];

  if (!step) {
    return null;
  }

  const StepComponent = step.component;
  const isFirst = index === 0;
  const isLast = index === registeredSteps.length - 1;

  return (
    <main className="mx-auto flex min-h-screen max-w-3xl flex-col gap-6 px-6 py-10">
      <header>
        <p className="text-sm text-slate-500">
          Step {index + 1} of {registeredSteps.length}
        </p>
        <h1 className="text-2xl font-semibold text-slate-950">{step.title}</h1>
      </header>
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <StepComponent />
      </section>
      <nav className="flex items-center justify-between">
        <button
          className="rounded bg-slate-200 px-4 py-2 text-sm font-medium text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isFirst}
          onClick={() => setIndex((current) => Math.max(current - 1, 0))}
          type="button"
        >
          Back
        </button>
        <button
          className="rounded bg-slate-950 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
          disabled={isLast}
          onClick={() =>
            setIndex((current) => Math.min(current + 1, registeredSteps.length - 1))
          }
          type="button"
        >
          Next
        </button>
      </nav>
    </main>
  );
}
