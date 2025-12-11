import { headers } from 'next/headers';
import PageRenderer from '@/lib/pageRenderer';
import { loadPageSchema } from '@/lib/schemaLoader';
import type { UiContext } from '@/lib/ai/uiOrchestrator';

export default async function ToolDiscoveryPage() {
  const schema = await loadPageSchema('/tools/discovery');
  if (!schema) return <div className="p-6 text-white">Tool discovery schema missing</div>;
  const hdrs = headers();
  const context: UiContext = {
    role: 'admin',
    featureFlags: process.env.FEATURE_LATENTBOX_RECOMMENDATIONS ? ['FEATURE_LATENTBOX_RECOMMENDATIONS'] : [],
    tenancyMode: 'multi',
    tenantId: hdrs.get('tenant-id') || undefined
  };
  return (
    <div className="p-6">
      <PageRenderer schema={schema} context={context} />
    </div>
  );
}
