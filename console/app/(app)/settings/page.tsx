import { GlassCard } from '../../../components/GlassCard';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <GlassCard title="Profile" description="Manage your account">
        <dl className="grid gap-4 text-sm text-slate-200 md:grid-cols-2">
          <div>
            <dt>Email</dt>
            <dd>user@example.com</dd>
          </div>
          <div>
            <dt>Role</dt>
            <dd>manager</dd>
          </div>
          <div>
            <dt>Tenant</dt>
            <dd>default</dd>
          </div>
          <div>
            <dt>API key</dt>
            <dd>Generate via CLI</dd>
          </div>
        </dl>
      </GlassCard>
      <GlassCard title="Security" description="Rotate credentials and configure MFA" />
    </div>
  );
}
