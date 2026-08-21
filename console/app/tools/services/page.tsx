import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function ServicesPage() {
  return (
    <CapabilityUnavailablePage
      title="Service manager"
      description="Manage supported OMERTAOS services."
      reason="The running Gateway does not expose service lifecycle commands. Start, stop, and restart controls are hidden to prevent false success."
    />
  );
}
