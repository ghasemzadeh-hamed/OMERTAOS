import { Box, Cpu, Layers3 } from 'lucide-react';

export function ModelsApp() {
  return (
    <div className="app-page">
      <header className="app-heading"><div><span className="section-label">Registry</span><h2>Models</h2></div></header>
      <div className="feature-list">
        <article className="feature-row"><span className="feature-icon"><Box size={20} /></span><div><h3>Model Registry</h3><p>Model metadata remains owned by the existing Console and Control Plane.</p></div><span className="status-text">Console-backed</span></article>
        <article className="feature-row"><span className="feature-icon"><Cpu size={20} /></span><div><h3>Local Models</h3><p>Runtime inventory will appear when capability endpoints are available.</p></div><span className="status-text">Pending</span></article>
        <article className="feature-row"><span className="feature-icon"><Layers3 size={20} /></span><div><h3>Routing Profiles</h3><p>Open Web Console for provider and routing configuration.</p></div><span className="status-text">Web Console</span></article>
      </div>
    </div>
  );
}
