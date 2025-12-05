import React from 'react';

interface ResourceLink {
  title: string;
  description: string;
  path: string;
}

const resources: ResourceLink[] = [
  {
    title: 'Bridge server (MCP over stdio)',
    description: 'TypeScript MCP host in WSL that proxies OMERTA gateway/control.',
    path: 'integrations/windows-agentic-bridge/bridge-server/',
  },
  {
    title: 'Bridge UI (React/Vite)',
    description: 'Minimal admin console for connection, tools exposure, and logs.',
    path: 'integrations/windows-agentic-bridge/bridge-ui/',
  },
  {
    title: 'Manifests',
    description: 'ODR manifest template for launching the bridge via wsl.exe.',
    path: 'integrations/windows-agentic-bridge/manifests/omertaos-wsl.mcp.json',
  },
  {
    title: 'Helper scripts',
    description: 'PowerShell/WSL scripts for registration, health checks, and startup.',
    path: 'integrations/windows-agentic-bridge/scripts/',
  },
  {
    title: 'Docs',
    description: 'Architecture, setup guides, and security notes with ASCII diagrams.',
    path: 'integrations/windows-agentic-bridge/docs/',
  },
];

const ResourceLinks: React.FC = () => {
  return (
    <section style={{ display: 'grid', gap: '0.75rem' }}>
      <h2 style={{ margin: 0, fontSize: '1.1rem' }}>Project map</h2>
      <div style={{ display: 'grid', gap: '0.5rem' }}>
        {resources.map((item) => (
          <div
            key={item.title}
            style={{
              border: '1px solid #e5e7eb',
              borderRadius: 8,
              padding: '0.75rem 1rem',
              background: '#f9fafb',
            }}
          >
            <div style={{ fontWeight: 600 }}>{item.title}</div>
            <div style={{ color: '#4b5563', fontSize: '0.95rem', margin: '0.25rem 0' }}>
              {item.description}
            </div>
            <code style={{ color: '#111827', fontSize: '0.9rem' }}>{item.path}</code>
          </div>
        ))}
      </div>
    </section>
  );
};

export default ResourceLinks;
