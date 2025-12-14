import React from 'react';
import OmertaConfigForm from '../components/OmertaConfigForm';
import ToolsExposureTable from '../components/ToolsExposureTable';

const Settings: React.FC = () => (
  <div style={{ display: 'grid', gap: '1rem' }}>
    <OmertaConfigForm />
    <ToolsExposureTable />
  </div>
);

export default Settings;
