import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function AgentDetailsPage() {
  return (
    <CapabilityUnavailablePage
      title="Agent details"
      description="Inspect a deployed agent instance."
      reason="The running Gateway does not expose agent instance detail endpoints."
    />
  );
}
