/**
 * Purpose: Application entry point that initializes and renders the React application
 * Scope: Handles application bootstrapping, error handling, and provider setup
 * Overview: This is the main entry file that sets up the React application with all necessary
 *           providers and error boundaries. It includes global error handling for uncaught
 *           errors and promise rejections, implements error storm protection, and renders
 *           the app within StrictMode for development safety.
 * Dependencies: React, React DOM, React Router, AppProviders, MinimalErrorBoundary, App component
 * Exports: No exports - this is an entry point file
 * Props/Interfaces: No props - bootstraps the application
 * State/Behavior: Sets up global error handlers, finds root DOM element, and renders app tree
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './styles/global.css';
import './index.css';
import App from './App.tsx';
import { AppProviders } from './app/AppProviders';
import { MinimalErrorBoundary } from './core/errors/MinimalErrorBoundary';

// Simplified global error handling for security/performance
let errorCount = 0;
let lastErrorTime = 0;
const ERROR_THRESHOLD = 5;
const TIME_WINDOW = 60000;

window.addEventListener('error', (event) => {
  const now = Date.now();
  if (now - lastErrorTime > TIME_WINDOW) errorCount = 0;
  errorCount++;
  lastErrorTime = now;

  if (errorCount >= ERROR_THRESHOLD) {
    console.error('Error storm detected, preventing cascade');
    return;
  }

  console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
  const now = Date.now();
  if (now - lastErrorTime > TIME_WINDOW) errorCount = 0;
  errorCount++;
  lastErrorTime = now;

  if (errorCount >= ERROR_THRESHOLD) {
    console.error('Promise rejection storm detected');
    return;
  }

  console.error('Unhandled promise rejection:', event.reason);
});

console.error('[main.tsx] Starting app initialization');

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('[main.tsx] Root element not found!');
  throw new Error('Failed to find root element');
}

console.error('[main.tsx] Root element found, rendering app');

createRoot(rootElement).render(
  <StrictMode>
    <MinimalErrorBoundary>
      <AppProviders>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </AppProviders>
    </MinimalErrorBoundary>
  </StrictMode>,
);
