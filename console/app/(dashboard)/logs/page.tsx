import GlassCard from '@/components/GlassCard';

export default function LogsPage() {
  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4">Logs</h2>
      <p className="opacity-80 text-sm">Stream structured logs from the Control API to audit actions and compliance events.</p>
    </GlassCard>
  );
}
