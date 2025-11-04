import GlassCard from '@/components/GlassCard';
import GovernanceDashboard from '@/components/GovernanceDashboard';
import WorkflowDesigner from '@/components/WorkflowDesigner';
import ChatPanel from '@/personal/ChatPanel';

type AgentStatus = 'online' | 'idle' | 'offline';

type AgentDescriptor = {
  name: string;
  description: string;
  status: AgentStatus;
  tags: string[];
};

const agentCatalog: AgentDescriptor[] = [
  {
    name: 'Research Agent',
    description: 'Synthesizes knowledge across internal and external sources.',
    status: 'online',
    tags: ['research', 'analysis'],
  },
  {
    name: 'Compliance Agent',
    description: 'Guards policies and tracks audit evidence.',
    status: 'idle',
    tags: ['governance', 'audit'],
  },
];

const statusTone: Record<AgentStatus, string> = {
  online: 'bg-emerald-500/80 text-emerald-50',
  idle: 'bg-amber-500/80 text-amber-50',
  offline: 'bg-slate-500/70 text-slate-100',
};

export default function DashboardHome() {
  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard className="space-y-4">
          <header className="space-y-1">
            <h2 className="text-xl font-semibold text-white">Workflow Designer</h2>
            <p className="text-sm text-white/70">Orchestrate multi-stage automations</p>
          </header>
          <WorkflowDesigner />
        </GlassCard>
        <GlassCard className="space-y-4">
          <header className="space-y-1">
            <h2 className="text-xl font-semibold text-white">Governance Overview</h2>
            <p className="text-sm text-white/70">Continuous compliance & risk posture</p>
          </header>
          <GovernanceDashboard />
        </GlassCard>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <GlassCard className="space-y-4">
          <header className="space-y-1">
            <h2 className="text-xl font-semibold text-white">Agent Catalog</h2>
            <p className="text-sm text-white/70">Review capabilities provisioned in AION-OS</p>
          </header>
          <div className="grid gap-4">
            {agentCatalog.map((agent) => (
              <article
                key={agent.name}
                className="rounded-xl border border-white/10 bg-white/5 p-4 shadow-lg backdrop-blur-md"
              >
                <header className="mb-2 flex items-center justify-between gap-2">
                  <h3 className="text-lg font-semibold text-white">{agent.name}</h3>
                  <span
                    className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${statusTone[agent.status]}`}
                  >
                    {agent.status.toUpperCase()}
                  </span>
                </header>
                <p className="text-sm text-white/70">{agent.description}</p>
                {agent.tags.length > 0 && (
                  <ul className="mt-3 flex flex-wrap gap-2 text-xs text-white/80">
                    {agent.tags.map((tag) => (
                      <li key={tag} className="rounded-full border border-white/10 bg-white/10 px-2 py-1">
                        #{tag}
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            ))}
          </div>
        </GlassCard>
        <GlassCard className="space-y-4">
          <header className="space-y-1">
            <h2 className="text-xl font-semibold text-white">Personal Mode</h2>
            <p className="text-sm text-white/70">Chat securely with your delegated copilot</p>
          </header>
          <ChatPanel />
        </GlassCard>
      </div>
    </div>
  );
}
