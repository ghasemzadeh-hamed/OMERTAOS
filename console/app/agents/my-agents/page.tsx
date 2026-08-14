import { headers } from 'next/headers';
import PageRenderer from '@/lib/pageRenderer';
import { loadPageSchema } from '@/lib/schemaLoader';
import type { UiContext } from '@/lib/ai/uiOrchestrator';

export default async function MyAgentsPage() {
  const schema = await loadPageSchema('/agents/my-agents');
  if (!schema) return <div className="p-6 text-white">My Agents schema missing</div>;
  const hdrs = await headers();
  const context: UiContext = {
    role: 'admin',
    featureFlags: [],
    tenancyMode: 'multi',
    tenantId: hdrs.get('tenant-id') || undefined
  };
  return (
    <div className="p-6">
      <PageRenderer schema={schema} context={context} />
    </div>
  );
}
