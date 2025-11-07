import type { ReactNode } from 'react';
import '@aionos/ui-core/src/theme/tokens.css';

export default function WizardLayout({ children }: { children: ReactNode }) {
  return <div className="wizard-shell">{children}</div>;
}
