import { GlassCard } from '../../../components/GlassCard';
import Link from 'next/link';

const projects = [
  { id: 'core', name: 'Core orchestration', description: 'Primary tenant configuration and routing policies.' },
  { id: 'research', name: 'Research playground', description: 'Experimental agents and hybrid flows.' },
];

export default function ProjectsPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      {projects.map((project) => (
        <GlassCard
          key={project.id}
          title={project.name}
          description={project.description}
          action={<Link className="glass-button" href={`/projects/${project.id}`}>View</Link>}
        />
      ))}
    </div>
  );
}
