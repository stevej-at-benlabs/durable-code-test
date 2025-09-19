/**
 * Purpose: Root application component - minimal shell
 * Scope: Application entry point
 * Overview: Clean separation of concerns with AppShell component
 * Dependencies: React, AppShell component
 * Exports: App component (default)
 * Props/Interfaces: No props - root component
 * Implementation: Minimal shell delegating to AppShell
 */

import './App.css';
import './qa-maintenance.css';
import { AppShell } from './components/AppShell/AppShell';

function App() {
  return <AppShell />;
}

export default App;
