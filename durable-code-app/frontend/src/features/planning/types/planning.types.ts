/**
 * Purpose: TypeScript type definitions for the planning feature module
 * Scope: Type definitions for planning resources, documents, and workflows
 * Overview: Centralized type definitions for planning-related data structures
 * Dependencies: None
 * Exports: PlanningDocument, PlanningCategory interfaces
 * Interfaces: PlanningDocument, PlanningCategory
 * Implementation: Type definitions for planning tab functionality
 */

export interface PlanningDocument {
  id: string;
  icon: string;
  title: string;
  description: string;
  href: string;
  badge: string;
  category: PlanningCategory;
}

export type PlanningCategory =
  | 'Essential'
  | 'Active'
  | 'Strategic'
  | 'Technical'
  | 'Quality'
  | 'Visual'
  | 'Timeline';

export interface PlanningSection {
  title: string;
  icon: string;
  subtitle: string;
  documents: PlanningDocument[];
}

// Case Study types for AWS deployment project
export interface CaseStudyStep {
  id: string;
  stepNumber: number;
  title: string;
  icon: string;
  subtitle: string;
  status: 'completed' | 'in-progress' | 'upcoming';
  popup: CaseStudyPopup;
}

export interface CaseStudyPopup {
  overview: {
    title: string;
    points: string[];
  };
  documents: {
    title: string;
    items: PopupDocument[];
  };
  implementation: {
    title: string;
    points: string[];
  };
  outcomes: {
    title: string;
    points: string[];
  };
  links?: PopupLink[];
}

export interface PopupDocument {
  name: string;
  description: string;
  purpose: string;
}

export interface PopupLink {
  text: string;
  url: string;
}

export interface CaseStudyData {
  title: string;
  subtitle: string;
  steps: CaseStudyStep[];
}

export interface UsePlanningReturn {
  planningSection: PlanningSection;
  caseStudy: CaseStudyData;
  loading: boolean;
  error: Error | null;
}
