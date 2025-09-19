/**
 * Purpose: Public exports for navigation feature module
 * Scope: Navigation feature barrel export
 * Overview: Central export point for navigation components and types
 * Dependencies: Navigation components and types
 * Exports: Navigation components and types
 * Implementation: Feature module barrel file
 */

export { TabNavigation } from './components/TabNavigation/TabNavigation';
export { useNavigation } from './hooks/useNavigation';
export type {
  TabName,
  TabContent,
  TabConfig,
  NavigationProps,
} from './types/navigation.types';
