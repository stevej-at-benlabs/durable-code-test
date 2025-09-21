/**
 * Purpose: Main application shell component providing routing structure and navigation between pages
 * Scope: Handles top-level application routing and page navigation
 * Overview: The AppShell component serves as the primary routing container for the application,
 * defining routes for HomePage, Standards, and CustomLinters pages. Each route is wrapped with
 * error boundaries to ensure robust error handling and prevent application crashes.
 * Dependencies: React Router DOM for routing, MinimalErrorBoundary for error handling, page components
 * Exports: AppShell functional component
 * Props/Interfaces: No props - uses React Router's location state for navigation
 * State/Behavior: Stateless component that renders different pages based on current route
 */

import type { ReactElement } from 'react';
import { Route, Routes } from 'react-router-dom';
import HomePage from '../../pages/HomePage/HomePage';
import Standards from '../../pages/Standards';
import CustomLinters from '../../pages/CustomLinters';
import { MinimalErrorBoundary } from '../../core/errors/MinimalErrorBoundary';

export function AppShell(): ReactElement {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <MinimalErrorBoundary>
            <HomePage />
          </MinimalErrorBoundary>
        }
      />
      <Route
        path="/standards"
        element={
          <MinimalErrorBoundary>
            <Standards />
          </MinimalErrorBoundary>
        }
      />
      <Route
        path="/custom-linters"
        element={
          <MinimalErrorBoundary>
            <CustomLinters />
          </MinimalErrorBoundary>
        }
      />
    </Routes>
  );
}
