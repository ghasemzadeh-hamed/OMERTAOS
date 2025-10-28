import GlassCard from '@/components/GlassCard';

export default function DashboardHome() {
  return (
    <div className="grid gap-6 md:grid-cols-3">
      <GlassCard>
        <div className="text-sm opacity-70 mb-2">System</div>
        <div className="text-3xl font-semibold">Overview</div>
        <div className="mt-4 opacity-80">Quick health &amp; stats</div>
      </GlassCard>
      <GlassCard>
        <div className="text-sm opacity-70 mb-2">Tasks</div>
        <div className="text-3xl font-semibold">Live Stream</div>
        <div className="mt-4 opacity-80">Connect SSE/WS to Gateway</div>
      </GlassCard>
      <GlassCard>
        <div className="text-sm opacity-70 mb-2">Agents</div>
        <div className="text-3xl font-semibold">Registry</div>
        <div className="mt-4 opacity-80">Manage modules &amp; policies</div>
      </GlassCard>
    </div>
  );
}
