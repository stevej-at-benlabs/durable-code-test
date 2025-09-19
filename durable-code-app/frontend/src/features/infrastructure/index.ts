/**
 * Purpose: Main entry point for infrastructure feature module
 * Scope: Feature-level exports for infrastructure components, hooks, and types
 * Overview: Barrel export for entire infrastructure feature providing clean
 *     imports for external components. Exports main components, hooks, and types
 *     needed by other parts of the application.
 * Dependencies: Infrastructure components, hooks, and types
 * Exports: InfrastructureTab (default), hooks, types, and utilities
 */

// Components
export {
  default as InfrastructureTab,
  InfrastructureTab as InfrastructureTabComponent,
} from './components/InfrastructureTab';

// Hooks
export { useInfrastructure } from './hooks/useInfrastructure';

// Types
export type {
  InfrastructureItem,
  FolderItem,
  MakeTarget,
  InfrastructureStats,
  ActionLink,
  InfrastructureTabProps,
  InfrastructureCardProps,
  FolderStructureProps,
  StatsDisplayProps,
  ActionLinksProps,
  UseInfrastructureReturn,
  InfrastructureCategory,
  BadgeType,
  LinkType,
  FolderItemType,
} from './types/infrastructure.types';

// Default export
export { default } from './components/InfrastructureTab';
