import React from 'react';

const demoLogs = [
  { level: 'info', message: 'Bridge initialized' },
  { level: 'debug', message: 'Tool registry hydrated' },
];

const LogsPanel: React.FC = () => (
  <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem', fontFamily: 'ui-monospace, SFMono-Regular' }}>
    <h3>Logs</h3>
    <div style={{ maxHeight: 240, overflowY: 'auto', background: '#0f172a', color: '#e2e8f0', padding: '0.75rem' }}>
      {demoLogs.map((log, idx) => (
        <div key={idx}>
          <strong>[{log.level}]</strong> {log.message}
        </div>
      ))}
    </div>
  </div>
);

export default LogsPanel;
