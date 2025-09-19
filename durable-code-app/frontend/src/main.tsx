/**
 * Purpose: Application entry point and root component mounting
 * Scope: React application bootstrap and router setup
 * Overview: Main entry point for the React application that sets up the root component tree
 *     with React Router for client-side navigation and React StrictMode for development
 *     assistance. Mounts the App component to the DOM root element and establishes the
 *     browser routing context for the entire application.
 * Dependencies: React (StrictMode, createRoot), React Router (BrowserRouter), App component
 * Exports: No exports - side effect only (DOM mounting)
 * State/Behavior: Immediately executes to mount React application on page load
 */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './styles/global.css';
import './index.css';
import App from './App.tsx';
import { AppProviders } from './app/AppProviders';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error('Failed to find root element');
}

createRoot(rootElement).render(
  <StrictMode>
    <AppProviders>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AppProviders>
  </StrictMode>,
);
