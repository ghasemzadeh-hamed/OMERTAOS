import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function LogsPage() {
  return (
    <CapabilityUnavailablePage
      title="Logs"
      description="Inspect audit and service logs."
      reason="The running Gateway does not expose a log stream or audit query endpoint."
    />
  );
}
