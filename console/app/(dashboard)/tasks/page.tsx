import GlassCard from '@/components/GlassCard';

export default function TasksPage() {
  return (
    <GlassCard>
      <h2 className="text-xl font-semibold mb-4">Tasks</h2>
      <div className="opacity-80 text-sm">
        Hook SSE from {process.env.NEXT_PUBLIC_GATEWAY_URL}/v1/stream/:id or proxy through Next.js for streaming telemetry.
      </div>
    </GlassCard>
  );
}
