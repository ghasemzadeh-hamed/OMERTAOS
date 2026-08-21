import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function TasksPage() {
  return (
    <CapabilityUnavailablePage
      title="Tasks"
      description="Inspect submitted and completed work."
      reason="Task submission is available in Chat and Agent Mode, but the running Gateway does not expose a task-list endpoint."
    />
  );
}
