import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Import Ant Design styles
import 'antd/dist/reset.css';

// Import global styles
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
