import RemoteCollectionPage from '@/components/RemoteCollectionPage';

export default function MyAgentsPage() {
  return (
    <RemoteCollectionPage
      endpoint="/api/system/agents"
      title="My agents"
      description="Inspect deployed agent instances reported by the Gateway."
      collectionKeys={['agents', 'instances', 'items']}
      emptyLabel="No agent instances have been deployed."
      itemHrefBase="/agents"
    />
  );
}
