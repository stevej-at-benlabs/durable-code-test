import type { HTMLAttributes, ReactNode } from 'react';

export type CardVariant = 'default' | 'feature' | 'stat' | 'principle';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  variant?: CardVariant;
  icon?: ReactNode;
  title?: string;
  badge?: string;
  clickable?: boolean;
  className?: string;
}
