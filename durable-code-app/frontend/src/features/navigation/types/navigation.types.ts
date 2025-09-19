/**
 * Purpose: Type definitions for navigation feature
 * Scope: Navigation-related types and interfaces
 * Overview: Centralized type definitions for navigation components
 * Dependencies: React types, navigation store
 * Exports: Navigation types and interfaces
 * Implementation: Strong typing for navigation feature
 */

import type { ComponentType, LazyExoticComponent } from 'react';
import type { TabName } from '../../../store/navigationStore';

export type { TabName };

export interface TabContent {
  title: string;
  icon: string;
  description: string;
  component: LazyExoticComponent<ComponentType>;
}

export interface TabConfig {
  tabs: Record<TabName, TabContent>;
}

export interface NavigationProps {
  activeTab: TabName;
  onTabChange: (tab: TabName) => void;
  tabs: Record<TabName, TabContent>;
}
