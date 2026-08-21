import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function MetricsPage() {
  return (
    <CapabilityUnavailablePage
      title="Metrics"
      description="Inspect platform metrics and monitoring integrations."
      reason="No source-backed metrics endpoint or configured dashboard is exposed by the running Gateway."
    />
  );
}
