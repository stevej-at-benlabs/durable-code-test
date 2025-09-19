/**
 * Purpose: Minimal app shell component
 * Scope: Root application shell with routing
 * Overview: Clean separation of routing from business logic
 * Dependencies: React Router, page components
 * Exports: AppShell component
 * Props/Interfaces: No props - root component
 * Implementation: Minimal shell with routes only
 */

import type { ReactElement } from 'react';
import { Route, Routes } from 'react-router-dom';
import HomePage from '../../pages/HomePage/HomePage';
import Standards from '../../pages/Standards';
import CustomLinters from '../../pages/CustomLinters';

export function AppShell(): ReactElement {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/standards" element={<Standards />} />
      <Route path="/custom-linters" element={<CustomLinters />} />
    </Routes>
  );
}
