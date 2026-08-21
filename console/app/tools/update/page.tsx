import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function UpdatePage() {
  return (
    <CapabilityUnavailablePage
      title="Update center"
      description="Check and apply OMERTAOS updates."
      reason="The running Gateway does not expose signed update metadata or an audited update executor. Check and apply controls are hidden."
    />
  );
}
