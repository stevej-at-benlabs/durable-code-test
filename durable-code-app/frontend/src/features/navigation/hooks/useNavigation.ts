/**
 * Purpose: Custom hook for navigation state and URL synchronization
 * Scope: Navigation logic and browser history management
 * Overview: Manages tab navigation and URL hash synchronization
 * Dependencies: React, React Router, navigation store
 * Exports: useNavigation custom hook
 * Implementation: Encapsulates navigation logic with URL handling
 */

import { useEffect } from 'react';
import { useNavigationStore } from '../../../store/navigationStore';
import type { TabName } from '../types/navigation.types';

export function useNavigation() {
  const { activeTab, setActiveTab } = useNavigationStore();

  const getInitialTab = (): TabName => {
    const hash = window.location.hash.replace('#', '');
    const urlParams = new URLSearchParams(window.location.search);
    const returnTab = urlParams.get('return');
    const validTabs: TabName[] = [
      'Repository',
      'Planning',
      'Building',
      'Quality Assurance',
      'Maintenance',
      'Demo',
    ];

    if (validTabs.includes(hash as TabName)) {
      return hash as TabName;
    }
    if (returnTab && validTabs.includes(returnTab as TabName)) {
      return returnTab as TabName;
    }
    return 'Repository';
  };

  useEffect(() => {
    const initialTab = getInitialTab();
    setActiveTab(initialTab);
  }, [setActiveTab]);

  useEffect(() => {
    const handlePopState = () => {
      const hash = window.location.hash.replace('#', '');
      const validTabs: TabName[] = [
        'Repository',
        'Planning',
        'Building',
        'Quality Assurance',
        'Maintenance',
        'Demo',
      ];
      if (validTabs.includes(hash as TabName)) {
        setActiveTab(hash as TabName);
      } else {
        setActiveTab('Repository');
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [setActiveTab]);

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const returnTab = urlParams.get('return');

    if (returnTab) {
      const newUrl = window.location.pathname + `#${activeTab}`;
      window.history.replaceState(null, '', newUrl);
    }
  }, [activeTab]);

  const handleTabChange = (tab: TabName) => {
    setActiveTab(tab);
  };

  return {
    activeTab,
    handleTabChange,
  };
}
