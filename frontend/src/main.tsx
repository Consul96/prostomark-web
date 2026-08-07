import React from 'react';
import ReactDOM from 'react-dom/client';

import { App } from './app/App';
import { captureNavigationTiming } from './shared/telemetry';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// Lightweight page-load diagnostics (Performance API). No-op unless a slow load
// is observed / telemetry is enabled. Never blocks rendering.
captureNavigationTiming();
