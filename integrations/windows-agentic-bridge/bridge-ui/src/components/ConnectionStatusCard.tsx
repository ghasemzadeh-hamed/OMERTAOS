import React from 'react';

type Status = 'ok' | 'warn' | 'error' | 'unknown';

interface Props {
  title: string;
  status: Status;
  detail: string;
}

const colorMap: Record<Status, string> = {
  ok: '#10b981',
  warn: '#f59e0b',
  error: '#ef4444',
  unknown: '#6b7280',
};

const ConnectionStatusCard: React.FC<Props> = ({ title, status, detail }) => (
  <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem', minWidth: 240 }}>
    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
      <span style={{ width: 10, height: 10, borderRadius: '50%', background: colorMap[status], display: 'inline-block' }} />
      <strong>{title}</strong>
    </div>
    <p style={{ marginTop: '0.5rem', color: '#475569' }}>{detail}</p>
  </div>
);

export default ConnectionStatusCard;
