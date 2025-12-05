import React from 'react';

interface Props {
  current: 'dashboard' | 'settings' | 'logs' | 'about';
  onNavigate: (page: Props['current']) => void;
  children: React.ReactNode;
}

const Layout: React.FC<Props> = ({ current, onNavigate, children }) => {
  return (
    <div style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '1rem' }}>
      <header
        style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '1rem',
          alignItems: 'center',
          flexWrap: 'wrap',
        }}
      >
        {[
          ['dashboard', 'Dashboard'],
          ['settings', 'Settings'],
          ['logs', 'Logs'],
          ['about', 'About'],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => onNavigate(key as Props['current'])}
            style={{
              padding: '0.5rem 1rem',
              background: current === key ? '#111' : '#f3f4f6',
              color: current === key ? 'white' : '#111',
              border: '1px solid #e5e7eb',
              borderRadius: 6,
              cursor: 'pointer',
            }}
          >
            {label}
          </button>
        ))}
        <a
          href="../docs/README.md"
          style={{
            padding: '0.5rem 1rem',
            borderRadius: 6,
            border: '1px solid #e5e7eb',
            color: '#111',
            textDecoration: 'none',
            background: '#fff',
            marginLeft: 'auto',
          }}
        >
          Docs index
        </a>
      </header>
      <main>{children}</main>
    </div>
  );
};

export default Layout;
