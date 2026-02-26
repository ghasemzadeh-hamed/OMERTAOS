import React, { useState } from 'react';

const OmertaConfigForm: React.FC = () => {
  const [gatewayUrl, setGatewayUrl] = useState('http://localhost:3000');
  const [controlUrl, setControlUrl] = useState('http://localhost:8000');
  const [token, setToken] = useState('');
  const [message, setMessage] = useState('Not saved');

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem' }}>
      <h3>OMERTA Connection</h3>
      <label style={{ display: 'block', marginBottom: '0.5rem' }}>
        Gateway URL
        <input value={gatewayUrl} onChange={(e) => setGatewayUrl(e.target.value)} style={{ width: '100%', marginTop: 4 }} />
      </label>
      <label style={{ display: 'block', marginBottom: '0.5rem' }}>
        Control URL
        <input value={controlUrl} onChange={(e) => setControlUrl(e.target.value)} style={{ width: '100%', marginTop: 4 }} />
      </label>
      <label style={{ display: 'block', marginBottom: '0.5rem' }}>
        Admin Token
        <input
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          style={{ width: '100%', marginTop: 4 }}
        />
      </label>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button
          onClick={() => setMessage('Settings saved locally (mock).')}
          style={{ padding: '0.5rem 1rem', borderRadius: 6, border: '1px solid #111', cursor: 'pointer' }}
        >
          Save
        </button>
        <button
          onClick={() => setMessage(`Tested ${gatewayUrl} / ${controlUrl}`)}
          style={{ padding: '0.5rem 1rem', borderRadius: 6, border: '1px solid #111', cursor: 'pointer', background: '#e5e7eb' }}
        >
          Test connection
        </button>
      </div>
      <p style={{ marginTop: '0.5rem', color: '#475569' }}>{message}</p>
    </div>
  );
};

export default OmertaConfigForm;
