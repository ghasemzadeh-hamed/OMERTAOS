import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function DataStudioPage() {
  return (
    <CapabilityUnavailablePage
      title="Data studio"
      description="Preview structured workflow data."
      reason="The running Gateway does not expose a data-preview endpoint. The Console will not read host files directly."
    />
  );
}
