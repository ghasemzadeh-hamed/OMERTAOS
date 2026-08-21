import CapabilityUnavailablePage from "@/components/CapabilityUnavailablePage";

export default function DatasetsPage() {
  return (
    <CapabilityUnavailablePage
      title="Datasets"
      description="Register and index RAG datasets."
      reason="The running Gateway does not expose dataset ingestion endpoints. Upload and deletion controls are hidden."
    />
  );
}
