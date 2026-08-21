import CapabilityUnavailablePage from '@/components/CapabilityUnavailablePage';

export default function AdminTenancyPage() {
  return (
    <CapabilityUnavailablePage
      title="Tenancy administration"
      description="Tenant-level configuration and isolation controls."
      reason="The running Gateway does not expose a tenancy administration endpoint. No changes can be applied from this Console build."
    />
  );
}
