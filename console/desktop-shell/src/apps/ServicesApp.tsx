import { Database, Network, ServerCog } from 'lucide-react';

const services = ['Gateway', 'Control Plane', 'Runtime Daemon', 'Data Services'];

export function ServicesApp() {
  return (
    <div className="app-page">
      <header className="app-heading"><div><span className="section-label">Operations</span><h2>Services</h2></div></header>
      <div className="service-table">
        {services.map((service, index) => {
          const Icon = index === 0 ? Network : index === 3 ? Database : ServerCog;
          return <div className="service-row" key={service}><Icon size={18} /><strong>{service}</strong><span>Managed by OMERTAOS</span><span className="status-text">Observe only</span></div>;
        })}
      </div>
    </div>
  );
}
