import React from 'react';
import ConnectionStatusCard from '../components/ConnectionStatusCard';
import ToolsExposureTable from '../components/ToolsExposureTable';
import ResourceLinks from '../components/ResourceLinks';

const Dashboard: React.FC = () => {
  return (
    <div style={{ display: 'grid', gap: '1rem' }}>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <ConnectionStatusCard title="OMERTA Status" status="unknown" detail="Configure endpoints to view health." />
        <ConnectionStatusCard title="Bridge Status" status="ok" detail="Bridge UI is reachable." />
      </div>
      <ResourceLinks />
      <ToolsExposureTable />
    </div>
  );
};

export default Dashboard;
