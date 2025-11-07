'use client';

import { useMemo, useState } from 'react';
import { getSteps } from './registry';

export default function WizardRouter() {
  const steps = useMemo(() => getSteps(), []);
  const [index, setIndex] = useState(0);
  const active = steps[index];
  const Step = active?.component ?? (() => null);

  return (
    <div className="aionos-wizard">
      <div className="head">
        <h1>{active?.title ?? ''}</h1>
      </div>
      <Step />
      <div className="nav">
        <button disabled={index === 0} onClick={() => setIndex((i) => Math.max(i - 1, 0))}>
          Back
        </button>
        <button
          disabled={index >= steps.length - 1}
          onClick={() => setIndex((i) => Math.min(i + 1, steps.length - 1))}
        >
          Next
        </button>
      </div>
    </div>
  );
}
