import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="section">
      <h2>Dashboard</h2>
      <p>Welcome to RAG System Dashboard!</p>
      <div style={{ marginTop: 20 }}>
        <h3>Quick Stats</h3>
        <ul>
          <li>Total Documents: 0</li>
          <li>Total Chunks: 0</li>
          <li>Active Sessions: 0</li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
