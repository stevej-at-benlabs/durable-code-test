import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type TabName =
  | 'Repository'
  | 'Planning'
  | 'Building'
  | 'Quality Assurance'
  | 'Maintenance'
  | 'Demo';

interface NavigationState {
  activeTab: TabName;
  tabHistory: TabName[];
  setActiveTab: (tab: TabName) => void;
  navigateBack: () => void;
}

export const useNavigationStore = create<NavigationState>()(
  devtools(
    (set, get) => ({
      activeTab: 'Repository',
      tabHistory: [],
      setActiveTab: (tab) => {
        const { tabHistory } = get();
        set({
          activeTab: tab,
          tabHistory: [...tabHistory, tab],
        });
        window.history.pushState(null, '', `#${tab}`);
      },
      navigateBack: () => {
        const { tabHistory } = get();
        if (tabHistory.length > 1) {
          const newHistory = [...tabHistory];
          newHistory.pop();
          const previousTab = newHistory[newHistory.length - 1] || 'Repository';
          set({
            activeTab: previousTab,
            tabHistory: newHistory,
          });
          window.history.pushState(null, '', `#${previousTab}`);
        }
      },
    }),
    { name: 'navigation-store' },
  ),
);
