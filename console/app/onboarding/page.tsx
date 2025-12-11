import { headers } from 'next/headers';
import PageRenderer from '@/lib/pageRenderer';
import { loadPageSchema } from '@/lib/schemaLoader';
import type { UiContext } from '@/lib/ai/uiOrchestrator';

export default async function OnboardingPage() {
  const schema = await loadPageSchema('/onboarding');
  if (!schema) return <div className="p-6 text-white">Onboarding schema missing</div>;
  const hdrs = headers();
  const context: UiContext = {
    role: 'admin',
    featureFlags: [],
    tenancyMode: 'single',
    tenantId: hdrs.get('tenant-id') || undefined,
    setupDone: true,
    onboardingComplete: false
  };
  return (
    <div className="p-6">
      <PageRenderer schema={schema} context={context} />
    </div>
  );
}
