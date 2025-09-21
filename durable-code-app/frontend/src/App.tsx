/**
 * Purpose: Main application component that serves as the root of the React application
 * Scope: Top-level application wrapper that renders the primary application shell
 * Overview: The App component is the entry point for the user interface, responsible for
 *           rendering the AppShell component which contains the main application layout.
 *           It imports necessary CSS for styling and QA maintenance styles.
 * Dependencies: React, AppShell component, App.css and qa-maintenance.css stylesheets
 * Exports: App component as default export
 * Props/Interfaces: No props - this is a top-level component
 * State/Behavior: Stateless functional component that delegates all functionality to AppShell
 */

import './App.css';
import './qa-maintenance.css';
import { AppShell } from './components/AppShell/AppShell';

function App() {
  return <AppShell />;
}

export default App;
