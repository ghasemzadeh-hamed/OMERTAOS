import { headers } from 'next/headers';
import PageRenderer from '@/lib/pageRenderer';
import { loadPageSchema } from '@/lib/schemaLoader';
import type { UiContext } from '@/lib/ai/uiOrchestrator';

export default async function AgentDetailsPage({ params }: { params: { id: string } }) {
  const schema = await loadPageSchema('/agents/[id]');
  if (!schema) return <div className="p-6 text-white">Agent schema missing</div>;
  const hdrs = headers();
  const context: UiContext = {
    role: 'admin',
    featureFlags: [],
    tenancyMode: 'multi',
    tenantId: hdrs.get('tenant-id') || undefined
  };
  return (
    <div className="p-6">
      <PageRenderer schema={schema} context={context} params={params} />
    </div>
  );
}
