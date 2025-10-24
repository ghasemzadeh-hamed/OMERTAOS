import { ChatTerminal } from '../../../components/ChatTerminal';
import { GlassCard } from '../../../components/GlassCard';

export default function TerminalPage() {
  return (
    <div className="space-y-6">
      <GlassCard title="Interactive ChatOps" description="Run operational commands with guardrails and live telemetry." />
      <ChatTerminal />
    </div>
  );
}
