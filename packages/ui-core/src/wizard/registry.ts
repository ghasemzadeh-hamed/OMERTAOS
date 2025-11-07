import type { FC } from 'react';

export type StepId =
  | 'welcome'
  | 'locale'
  | 'mode'
  | 'profile'
  | 'storage'
  | 'user'
  | 'summary'
  | 'install'
  | 'finish';

export type WizardStep = {
  id: StepId;
  title: string;
  component: FC;
  guard?: (ctx: unknown) => Promise<boolean> | boolean;
};

let steps: WizardStep[] = [];

export const registerSteps = (nextSteps: WizardStep[]) => {
  steps = nextSteps.slice();
};

export const getSteps = () => steps.slice();
