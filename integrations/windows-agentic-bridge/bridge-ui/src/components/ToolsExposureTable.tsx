import React, { useState } from 'react';

const initialTools = [
  { name: 'omerta.list_agents', category: 'platform', enabled: true },
  { name: 'omerta.get_health', category: 'platform', enabled: true },
  { name: 'omerta.run_agent_intent', category: 'business', enabled: true },
  { name: 'omerta.restart_component', category: 'admin', enabled: false },
];

const ToolsExposureTable: React.FC = () => {
  const [rows, setRows] = useState(initialTools);

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, padding: '1rem' }}>
      <h3>Tools Exposure</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ textAlign: 'left' }}>
            <th style={{ padding: '0.5rem' }}>Name</th>
            <th style={{ padding: '0.5rem' }}>Category</th>
            <th style={{ padding: '0.5rem' }}>Enabled</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.name}>
              <td style={{ padding: '0.5rem', borderTop: '1px solid #e5e7eb' }}>{row.name}</td>
              <td style={{ padding: '0.5rem', borderTop: '1px solid #e5e7eb', textTransform: 'capitalize' }}>{row.category}</td>
              <td style={{ padding: '0.5rem', borderTop: '1px solid #e5e7eb' }}>
                <input
                  type="checkbox"
                  checked={row.enabled}
                  onChange={() =>
                    setRows((prev) => prev.map((r) => (r.name === row.name ? { ...r, enabled: !r.enabled } : r)))
                  }
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ToolsExposureTable;
