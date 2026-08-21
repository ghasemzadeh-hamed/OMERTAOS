import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function EditorPage() {
  return (
    <CapabilityUnavailablePage
      title="Policy editor"
      description="Edit approved policy and configuration files."
      reason="The running Gateway does not expose a Runtime-backed file editing endpoint. Direct host writes are disabled."
    />
  );
}
