import Link from 'next/link';
import GlassCard from '@/components/GlassCard';

export default function AgentsPage() {
  return (
    <GlassCard className="space-y-3">
      <h2 className="text-xl font-semibold mb-4">Agents</h2>
      <p className="opacity-80 text-sm">
        Registry of deployed agents, capabilities, and ownership metadata. Use the Agent Catalog to browse templates like
        CrewAI, AutoGPT, and SuperAGI, then deploy them into your tenant with a guided wizard.
      </p>
      <div className="flex flex-wrap gap-3">
        <Link
          href="/agents/catalog"
          className="rounded-xl border border-white/15 bg-white/10 px-4 py-2 text-sm text-white/90 transition hover:bg-white/20"
        >
          Open Agent Catalog
        </Link>
        <Link
          href="/agents/my-agents"
          className="rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white/80 transition hover:bg-white/15"
        >
          View my Agents
        </Link>
      </div>
    </GlassCard>
  );
}
