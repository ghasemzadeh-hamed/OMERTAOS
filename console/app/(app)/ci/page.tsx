import { GlassCard } from '../../../components/GlassCard';
import { TerminalMenu, TerminalMenuItem } from '../../../components/TerminalMenu';
import { InstallerPanel, InstallerStep } from '../../../components/InstallerPanel';
import { PipelinePanel, PipelineRun } from '../../../components/PipelinePanel';

const terminalMenu: TerminalMenuItem[] = [
  {
    label: 'Bootstrap CI workspace',
    command: 'make ci-bootstrap',
    description: 'Provision ephemeral runners, secrets, and cached dependencies.',
  },
  {
    label: 'Run smoke tests',
    command: 'make ci-smoke',
    description: 'Execute fast validation flow for pull requests.',
  },
  {
    label: 'Publish OCI module',
    command: 'scripts/install_module.sh --publish --module summarize_text',
    description: 'Syncs the signed module artifact to the configured registry.',
  },
];

const installerSteps: InstallerStep[] = [
  {
    title: 'Fetch manifest',
    description: 'Downloaded manifest.yaml and SBOM from the registry.',
    status: 'success',
    duration: 'Completed in 2.1s',
  },
  {
    title: 'Verify signature',
    description: 'Cosign verification succeeded using organization root of trust.',
    status: 'success',
    duration: 'Completed in 3.4s',
  },
  {
    title: 'Sandbox runtime',
    description: 'Applying seccomp profile and resource isolation for module launch.',
    status: 'running',
    duration: 'Executing…',
  },
  {
    title: 'Deploy to edge nodes',
    description: 'Awaiting approval from change management workflow.',
    status: 'pending',
  },
];

const pipelineRuns: PipelineRun[] = [
  {
    name: 'Console build & lint',
    branch: 'main',
    status: 'success',
    duration: '3m 24s',
    triggeredBy: 'ci-bot',
  },
  {
    name: 'Control plane integration',
    branch: 'feature/runtime-metrics',
    status: 'running',
    duration: '6m 18s',
    triggeredBy: 'sora',
  },
  {
    name: 'Gateway release promotion',
    branch: 'release/v1.4.0',
    status: 'failed',
    duration: '8m 44s',
    triggeredBy: 'ci-bot',
  },
];

export default function CIPage() {
  return (
    <div className="space-y-6">
      <GlassCard title="CI terminal menu" description="Quick access to automation commands">
        <TerminalMenu items={terminalMenu} />
      </GlassCard>
      <GlassCard title="Installer workflow" description="Track secure module rollout status">
        <InstallerPanel steps={installerSteps} />
      </GlassCard>
      <GlassCard title="Pipeline panel" description="Latest CI/CD executions across services">
        <PipelinePanel runs={pipelineRuns} />
      </GlassCard>
    </div>
  );
}
