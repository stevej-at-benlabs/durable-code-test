/**
 * Purpose: Type definitions for infrastructure feature components and data structures
 * Scope: Infrastructure tab feature with cards, folder structure, and make targets
 * Overview: Comprehensive TypeScript interfaces for infrastructure feature implementation.
 *     Defines types for infrastructure cards, folder structure items, make targets,
 *     and component props to ensure type safety across the infrastructure feature.
 * Dependencies: None (pure TypeScript types)
 * Exports: InfrastructureItem, FolderItem, MakeTarget, and component prop interfaces
 * Props/Interfaces: Core data structures for infrastructure components
 * State/Behavior: Type definitions only, no runtime behavior
 */

export interface InfrastructureItem {
  id: string;
  icon: string;
  title: string;
  badge: 'Critical' | 'Important' | 'Optional' | 'Foundation' | 'Essential';
  category: 'automation' | 'quality' | 'ai' | 'security' | 'development' | 'structure' | 'infrastructure' | 'documentation' | 'resilience' | 'testing';
  popup?: {
    problem: {
      title: string;
      points: string[];
    };
    solution: {
      title: string;
      points: string[];
    };
    example: {
      title: string;
      language: string;
      code: string;
      file?: string;
    };
    links?: {
      text: string;
      url: string;
    }[];
  };
}

export interface FolderItem {
  id: string;
  type: 'folder' | 'file';
  name: string;
  icon: string;
  description?: string;
  depth: number;
  isLast?: boolean;
  parentIsLast?: boolean;
}

export interface MakeTarget {
  name: string;
  icon: string;
  description: string;
  category: 'testing' | 'building' | 'linting' | 'deployment' | 'maintenance';
  importance: 'critical' | 'important' | 'utility';
}

export interface InfrastructureStats {
  makeTargets: number;
  linterCategories: number;
  codeTemplates: number;
  dockerCoverage: string;
}

export interface ActionLink {
  id: string;
  url: string;
  text: string;
  icon: string;
  type: 'primary' | 'secondary';
  description?: string;
}

// Component prop interfaces
export interface InfrastructureTabProps {
  className?: string;
  onError?: (error: Error) => void;
}

export interface InfrastructureCardProps {
  item: InfrastructureItem;
  onClick?: (item: InfrastructureItem) => void;
  className?: string;
}

export interface FolderStructureProps {
  items: FolderItem[];
  title: string;
  icon: string;
  description?: string;
  benefits?: string[];
  aiHelper?: string;
  className?: string;
}

export interface StatsDisplayProps {
  stats: InfrastructureStats;
  className?: string;
}

export interface ActionLinksProps {
  links: ActionLink[];
  title: string;
  icon: string;
  className?: string;
}

// Hook return types
export interface UseInfrastructureReturn {
  infrastructureItems: InfrastructureItem[];
  folderStructure: FolderItem[];
  makeTargets: MakeTarget[];
  stats: InfrastructureStats;
  actionLinks: ActionLink[];
  loading: boolean;
  error: Error | null;
}

// Utility types
export type InfrastructureCategory = InfrastructureItem['category'];
export type BadgeType = InfrastructureItem['badge'];
export type LinkType = ActionLink['type'];
export type FolderItemType = FolderItem['type'];
