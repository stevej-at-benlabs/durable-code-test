/**
 * Purpose: Custom React hook for managing planning feature data and state
 * Scope: Planning documents, workflows, and resources management
 * Overview: Provides data and utilities for the planning feature components
 * Dependencies: React, planning types
 * Exports: usePlanning custom hook
 * Interfaces: Uses PlanningDocument, PlanningSection from types
 * Implementation: Returns planning documents organized by sections
 */

import { useMemo } from 'react';
import type { PlanningDocument, PlanningSection } from '../types/planning.types';

const PLANNING_DOCUMENTS: PlanningDocument[] = [
  {
    id: 'feature-index',
    icon: '📑',
    title: 'Feature Index',
    description: 'Complete index of all planning documents and artifacts',
    href: '/planning/feature-index.html',
    badge: 'Essential',
    category: 'Essential',
  },
  {
    id: 'metadata',
    icon: '📊',
    title: 'Feature Metadata',
    description: 'Project configuration, team members, and timeline details',
    href: '/planning/metadata.html',
    badge: 'Essential',
    category: 'Essential',
  },
  {
    id: 'progress',
    icon: '📈',
    title: 'Progress Tracking',
    description: 'Current status, weekly updates, and milestone tracking',
    href: '/planning/progress.html',
    badge: 'Active',
    category: 'Active',
  },
  {
    id: 'rollout',
    icon: '🚀',
    title: 'Rollout Plan',
    description: 'Deployment strategy, feature flags, and phased release schedule',
    href: '/planning/rollout-plan.html',
    badge: 'Strategic',
    category: 'Strategic',
  },
  {
    id: 'tech-spec',
    icon: '🔧',
    title: 'Technical Specification',
    description: 'Architecture overview, API endpoints, and integration details',
    href: '/planning/technical-spec.html',
    badge: 'Technical',
    category: 'Technical',
  },
  {
    id: 'testing',
    icon: '✅',
    title: 'Testing Plan',
    description: 'Test scenarios, QA checklist, and validation criteria',
    href: '/planning/testing-plan.html',
    badge: 'Quality',
    category: 'Quality',
  },
  {
    id: 'dev-flow',
    icon: '🔄',
    title: 'Development Flow',
    description:
      'Visual workflow showing the complete development lifecycle with AI integration points',
    href: '/diagrams/durable-code-flow.html?return=Planning',
    badge: 'Visual',
    category: 'Visual',
  },
  {
    id: 'ai-review',
    icon: '📋',
    title: 'AI Review Sequence',
    description: 'Step-by-step sequence diagram for AI code review processes',
    href: '/diagrams/ai-review-sequence.html?return=Planning',
    badge: 'Visual',
    category: 'Visual',
  },
  {
    id: 'implementation',
    icon: '📅',
    title: 'Implementation Plan',
    description: 'Gantt chart showing project timeline and milestones',
    href: '/diagrams/implementation-plan.html?return=Planning',
    badge: 'Timeline',
    category: 'Timeline',
  },
];

export function usePlanning() {
  const planningSection: PlanningSection = useMemo(
    () => ({
      title: 'Planning Documents',
      icon: '📋',
      subtitle:
        'Effective planning is crucial for successful AI-assisted development. Our planning documents provide comprehensive guidance for project setup and execution.',
      documents: PLANNING_DOCUMENTS,
    }),
    [],
  );

  return {
    planningSection,
    documents: PLANNING_DOCUMENTS,
  };
}
