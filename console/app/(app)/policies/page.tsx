import { GlassCard } from '../../../components/GlassCard';
import { PolicyEditor } from '../../../components/PolicyEditor';
import { useTranslations } from 'next-intl';

export default function PoliciesPage() {
  const t = useTranslations('policies');
  return (
    <div className="space-y-6">
      <GlassCard title={t('title')} description="Adjust runtime budgets and latency guardrails">
        <PolicyEditor />
      </GlassCard>
    </div>
  );
}
