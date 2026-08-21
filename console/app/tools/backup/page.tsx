import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function BackupPage() {
  return (
    <CapabilityUnavailablePage
      title="Backup and snapshot"
      description="Create and inspect platform backups."
      reason="The running Gateway does not expose a backup API. Backup controls are hidden until execution and audit evidence are available."
    />
  );
}
