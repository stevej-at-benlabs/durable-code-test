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
