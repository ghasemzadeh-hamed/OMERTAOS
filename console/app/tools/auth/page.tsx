import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function AuthToolsPage() {
  return (
    <CapabilityUnavailablePage
      title="Auth and roles"
      description="Manage RBAC roles and scoped tokens."
      reason="Authentication is active, but the running Gateway does not expose user, role, or token administration endpoints."
    />
  );
}
