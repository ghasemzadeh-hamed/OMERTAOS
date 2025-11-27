'use client';

import { registerSteps, WizardRouter } from '@aionos/ui-core';

import Finish from './steps/09-finish';
import Install from './steps/08-install';
import Locale from './steps/02-locale';
import Mode from './steps/03-mode';
import Profile from './steps/04-profile';
import Storage from './steps/05-storage';
import Summary from './steps/07-summary';
import User from './steps/06-user';
import Welcome from './steps/01-welcome';

registerSteps([
  { id: 'welcome', title: 'Welcome', component: Welcome },
  { id: 'locale', title: 'Locale', component: Locale },
  { id: 'mode', title: 'Install Mode', component: Mode },
  { id: 'profile', title: 'Profile', component: Profile },
  { id: 'storage', title: 'Storage', component: Storage },
  { id: 'user', title: 'User', component: User },
  { id: 'summary', title: 'Summary', component: Summary },
  { id: 'install', title: 'Install', component: Install },
  { id: 'finish', title: 'Finish', component: Finish },
]);

export default function WizardClient() {
  return <WizardRouter />;
}
