/**
 * Purpose: Reusable feature card component for all tabs
 * Scope: Common component for displaying feature items with icon, title, description
 * Overview: Standardized card component with theme-aware styling and color variants
 * Dependencies: React, CSS Modules
 * Exports: FeatureCard component
 * Props/Interfaces: icon, title, description, children, variant, className
 * Implementation: Shared component with color theme variants
 */

import type { ReactElement, ReactNode } from 'react';
import styles from './FeatureCard.module.css';

export type FeatureCardVariant =
  | 'primary' // Default blue theme
  | 'success' // Green theme
  | 'warning' // Orange/yellow theme
  | 'info' // Blue theme
  | 'purple' // Purple theme
  | 'cyan' // Cyan theme
  | 'gold'; // Gold theme

interface FeatureCardProps {
  icon: string;
  title: string;
  description?: string;
  children?: ReactNode;
  variant?: FeatureCardVariant;
  className?: string;
}

export function FeatureCard({
  icon,
  title,
  description,
  children,
  variant = 'primary',
  className = '',
}: FeatureCardProps): ReactElement {
  return (
    <div className={`${styles.featureCard} ${styles[variant]} ${className}`}>
      <div className={styles.icon}>{icon}</div>
      <h5 className={styles.title}>{title}</h5>
      {description && <p className={styles.description}>{description}</p>}
      {children && <div className={styles.content}>{children}</div>}
    </div>
  );
}
