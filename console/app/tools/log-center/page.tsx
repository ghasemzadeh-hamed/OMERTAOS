import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function LogCenterPage() {
  return (
    <CapabilityUnavailablePage
      title="Log center"
      description="Search and stream aggregated logs."
      reason="The running Gateway does not expose a log collection endpoint. The Console will not fabricate or read container logs directly."
    />
  );
}
