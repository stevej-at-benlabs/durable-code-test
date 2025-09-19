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
