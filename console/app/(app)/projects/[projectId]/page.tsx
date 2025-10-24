import { GlassCard } from '../../../../components/GlassCard';
import { notFound } from 'next/navigation';

const projectMap: Record<string, { name: string; description: string; owners: string[] }> = {
  core: {
    name: 'Core orchestration',
    description: 'Production routing policies and guardrails.',
    owners: ['ops@aionos.local', 'security@aionos.local'],
  },
  research: {
    name: 'Research playground',
    description: 'Experimental agents and evaluation harness.',
    owners: ['research@aionos.local'],
  },
};

export default function ProjectDetail({ params }: { params: { projectId: string } }) {
  const project = projectMap[params.projectId];
  if (!project) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <GlassCard title={project.name} description={project.description}>
        <ul className="space-y-2 text-sm text-slate-200">
          {project.owners.map((owner) => (
            <li key={owner}>Owner: {owner}</li>
          ))}
        </ul>
      </GlassCard>
      <GlassCard title="Pipelines" description="Latest automation runs">
        <ul className="text-sm text-slate-200">
          <li>Daily feature build — success</li>
          <li>Weekly router training — queued</li>
        </ul>
      </GlassCard>
    </div>
  );
}
