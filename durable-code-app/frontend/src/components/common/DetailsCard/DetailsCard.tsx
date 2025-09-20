/**
 * Purpose: Reusable details card component for all tabs
 * Scope: Common component for displaying detailed content sections
 * Overview: Standardized card component with consistent styling across all features
 * Dependencies: React, CSS Modules
 * Exports: DetailsCard component
 * Props/Interfaces: title, icon, children, className
 * Implementation: Shared component with theme-aware styling
 */

import { memo } from 'react';
import type { ReactNode } from 'react';
import styles from './DetailsCard.module.css';

interface DetailsCardProps {
  title: string;
  icon: string;
  children: ReactNode;
  className?: string;
}

export const DetailsCard = memo<DetailsCardProps>(
  ({ title, icon, children, className = '' }) => {
    return (
      <div className={`${styles.detailsCard} ${className}`}>
        <h4 className={styles.title}>
          <span className={styles.icon}>{icon}</span>
          {title}
        </h4>
        <div className={styles.content}>{children}</div>
      </div>
    );
  },
);

DetailsCard.displayName = 'DetailsCard';
