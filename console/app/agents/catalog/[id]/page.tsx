import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function AgentTemplatePage() {
  return (
    <CapabilityUnavailablePage
      title="Agent template"
      description="Configure and deploy an agent template."
      reason="The running Gateway does not expose agent template or deployment endpoints."
    />
  );
}
