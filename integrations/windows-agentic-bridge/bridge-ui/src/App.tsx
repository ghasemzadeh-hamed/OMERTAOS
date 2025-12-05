import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import Settings from './pages/Settings';
import Logs from './pages/Logs';
import About from './pages/About';
import Layout from './components/Layout/Layout';

type Page = 'dashboard' | 'settings' | 'logs' | 'about';

const App: React.FC = () => {
  const [page, setPage] = useState<Page>('dashboard');

  return (
    <Layout current={page} onNavigate={setPage}>
      {page === 'dashboard' && <Dashboard />}
      {page === 'settings' && <Settings />}
      {page === 'logs' && <Logs />}
      {page === 'about' && <About />}
    </Layout>
  );
};

export default App;
