import type { ReactNode } from 'react';
import '@aionos/ui-core/theme/tokens.css';

export default function WizardLayout({ children }: { children: ReactNode }) {
  return <div className="aionos-wizard">{children}</div>;
}
