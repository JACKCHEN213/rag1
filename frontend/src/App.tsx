import React from 'react';
import { ConfigProvider, theme } from 'antd';

// Import pages
import Dashboard from './pages/Dashboard';
import DocumentManager from './pages/DocumentManager';
import Configuration from './pages/Configuration';

const App: React.FC = () => {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <div className="app">
        <h1>RAG System</h1>
        <Dashboard />
        <DocumentManager />
        <Configuration />
      </div>
    </ConfigProvider>
  );
};

export default App;
