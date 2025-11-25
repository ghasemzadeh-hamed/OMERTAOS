import GlassCard from '@/components/GlassCard';

export default function HealthPage() {
  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4">Health</h2>
      <p className="opacity-80 text-sm">Poll {process.env.NEXT_PUBLIC_GATEWAY_URL}/v1/health for orchestrator and gateway liveness.</p>
    </GlassCard>
  );
}
