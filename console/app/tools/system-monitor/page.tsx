import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function SystemMonitorPage() {
  return (
    <CapabilityUnavailablePage
      title="System monitor"
      description="Inspect source-backed host resource metrics."
      reason="The running Gateway exposes service health but not host CPU, memory, disk, or GPU metrics. Use System health for the available telemetry."
    />
  );
}
