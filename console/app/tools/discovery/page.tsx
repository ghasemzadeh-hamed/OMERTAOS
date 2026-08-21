import CapabilityUnavailablePage from '@/components/CapabilityUnavailablePage';

export default function ToolDiscoveryPage() {
  return (
    <CapabilityUnavailablePage
      title="Tool discovery"
      description="Discover tool providers registered with OMERTAOS."
      reason="The running Gateway does not expose a tool discovery endpoint. The Console will not fabricate a catalog without a source-backed response."
    />
  );
}
