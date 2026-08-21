import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function OnboardingPage() {
  return (
    <CapabilityUnavailablePage
      title="Onboarding"
      description="Configure post-setup organization onboarding."
      reason="Initial system setup is available, but the running Gateway does not expose post-setup onboarding endpoints."
    />
  );
}
