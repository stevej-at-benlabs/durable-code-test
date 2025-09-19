import type { HTMLAttributes } from 'react';

export type LoadingSpinnerSize = 'small' | 'medium' | 'large';
export type LoadingSpinnerVariant = 'primary' | 'secondary' | 'light';

export interface LoadingSpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: LoadingSpinnerSize;
  variant?: LoadingSpinnerVariant;
  className?: string;
  label?: string;
}
