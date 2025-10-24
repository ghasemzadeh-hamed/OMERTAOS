import { ModuleTable } from '../../../components/ModuleTable';
import { GlassCard } from '../../../components/GlassCard';

const modules = [
  {
    name: 'summarize_text',
    runtime: 'WASM (WASI)',
    version: '1.2.0',
    intents: ['summarize', 'explain'],
    gpu: 'CPU',
  },
  {
    name: 'invoice_ocr',
    runtime: 'Rust subprocess',
    version: '0.9.1',
    intents: ['invoice_ocr'],
    gpu: 'GPU optional',
  },
];

export default function AgentsPage() {
  return (
    <div className="space-y-6">
      <GlassCard title="Registered modules" description="Local runtimes signed via Cosign">
        <ModuleTable modules={modules} />
      </GlassCard>
      <GlassCard title="OCI registry" description="Use scripts/install_module.sh to sync" />
    </div>
  );
}
