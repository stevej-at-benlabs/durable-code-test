/**
 * Purpose: Main entry point for repository feature module
 * Scope: Feature-level exports for repository components, hooks, and types
 * Overview: Barrel export for entire repository feature providing clean
 *     imports for external components. Exports main components, hooks, and types
 *     needed by other parts of the application.
 * Dependencies: Repository components, hooks, and types
 * Exports: RepositoryTab (default), hooks, types, and utilities
 */

// Components
export {
  default as RepositoryTab,
  RepositoryTab as RepositoryTabComponent,
} from './components/RepositoryTab';

// Hooks
export { useRepository } from './hooks/useRepository';

// Types
export type {
  RepositoryItem,
  FolderItem,
  MakeTarget,
  RepositoryStats,
  ActionLink,
  RepositoryTabProps,
  RepositoryCardProps,
  FolderStructureProps,
  StatsDisplayProps,
  ActionLinksProps,
  UseRepositoryReturn,
  RepositoryCategory,
  BadgeType,
  LinkType,
  FolderItemType,
} from './types/repository.types';

// Default export
export { default } from './components/RepositoryTab';
