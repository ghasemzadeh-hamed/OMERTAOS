import type { ReactNode } from 'react';
import '@aion/ui-core/theme/tokens.css';

export default function WizardLayout({ children }: { children: ReactNode }) {
  return <div className="aion-wizard">{children}</div>;
}
