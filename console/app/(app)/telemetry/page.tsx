import { GlassCard } from '../../../components/GlassCard';
import { LogStream } from '../../../components/LogStream';

export default function TelemetryPage() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <GlassCard title="Grafana" description="Embedded dashboards">
        <iframe
          title="Grafana Router Overview"
          className="h-64 w-full rounded-3xl border border-white/10"
          src="http://localhost:3001/d/router-overview?orgId=1&kiosk"
        />
      </GlassCard>
      <GlassCard title="Live control logs" description="Streamed via OTEL collector">
        <LogStream endpoint="/api/proxy/stream/control" />
      </GlassCard>
    </div>
  );
}
