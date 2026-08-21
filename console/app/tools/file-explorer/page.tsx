import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function FileExplorerPage() {
  return (
    <CapabilityUnavailablePage
      title="File explorer"
      description="Browse approved workspace paths."
      reason="The running Gateway does not expose a sandboxed file API. File operations are hidden instead of bypassing the Runtime boundary."
    />
  );
}
