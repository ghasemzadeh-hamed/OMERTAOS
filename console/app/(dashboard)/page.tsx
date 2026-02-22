import GlassCard from '@/components/GlassCard';
import ChatPanel from '@/personal/ChatPanel';

export default function DashboardHome() {
  return (
    <div className="space-y-6">
      <GlassCard className="space-y-4 border border-cyan-300/20 bg-gradient-to-br from-slate-900/70 via-cyan-900/20 to-indigo-950/30">
        <header className="space-y-1">
          <h2 className="text-2xl font-semibold text-white">DastیارAI</h2>
          <p className="text-sm text-cyan-100/80">Your default language-model assistant on first dashboard view.</p>
        </header>
        <ChatPanel />
      </GlassCard>
    </div>
  );
}
