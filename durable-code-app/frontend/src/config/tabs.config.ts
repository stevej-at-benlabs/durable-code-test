/**
 * Purpose: Tab configuration for the application
 * Scope: Centralized tab definitions and lazy loading
 * Overview: Defines all application tabs and their components
 * Dependencies: React lazy loading, feature components
 * Exports: Tab configuration object
 * Implementation: Lazy-loaded feature tab configuration
 */

import { lazy } from 'react';
import type { TabContent, TabName } from '../features/navigation';

const InfrastructureTab = lazy(() =>
  import('../features/infrastructure').then((m) => ({
    default: m.InfrastructureTab,
  })),
);

const PlanningTab = lazy(() =>
  import('../features/planning').then((m) => ({
    default: m.PlanningTab,
  })),
);

const BuildingTab = lazy(() =>
  import('../features/building').then((m) => ({
    default: m.BuildingTab,
  })),
);

const QualityAssuranceTab = lazy(() =>
  import('../features/quality').then((m) => ({
    default: m.QualityAssuranceTab,
  })),
);

const MaintenanceTab = lazy(() =>
  import('../features/maintenance').then((m) => ({
    default: m.MaintenanceTab,
  })),
);

const DemoTab = lazy(() =>
  import('../features/demo').then((m) => ({
    default: m.DemoTab,
  })),
);

export const tabs: Record<TabName, TabContent> = {
  Infrastructure: {
    title: 'Infrastructure',
    icon: '🏗️',
    description: 'Building AI-ready projects with proper structure and context',
    component: InfrastructureTab,
  },
  Planning: {
    title: 'Planning',
    icon: '📋',
    description: 'Strategic planning and documentation for AI-assisted development',
    component: PlanningTab,
  },
  Building: {
    title: 'Building',
    icon: '🔨',
    description: 'Tools and commands for AI-assisted code generation',
    component: BuildingTab,
  },
  'Quality Assurance': {
    title: 'Quality Assurance',
    icon: '🛡️',
    description: 'Automated testing, linting, and CI/CD for code quality',
    component: QualityAssuranceTab,
  },
  Maintenance: {
    title: 'Maintenance',
    icon: '🔧',
    description: 'Ongoing maintenance and evolution strategies',
    component: MaintenanceTab,
  },
  Demo: {
    title: 'Demo',
    icon: '◉',
    description: 'Real-time oscilloscope demonstration with WebSocket streaming',
    component: DemoTab,
  },
};
