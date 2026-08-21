import RemoteCollectionPage from '@/components/RemoteCollectionPage';

export default function AgentCatalogPage() {
  return (
    <RemoteCollectionPage
      endpoint="/api/system/agents/catalog"
      title="Agent catalog"
      description="Browse agent templates reported by the Gateway."
      collectionKeys={['templates', 'catalog', 'agents', 'items']}
      emptyLabel="No agent templates are currently available."
      itemHrefBase="/agents/catalog"
    />
  );
}
