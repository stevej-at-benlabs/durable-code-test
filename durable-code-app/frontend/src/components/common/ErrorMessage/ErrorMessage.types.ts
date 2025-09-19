import type { HTMLAttributes, ReactNode } from 'react';

export type ErrorMessageVariant = 'error' | 'warning' | 'info';

export interface ErrorMessageProps extends HTMLAttributes<HTMLDivElement> {
  message: string;
  title?: string;
  variant?: ErrorMessageVariant;
  children?: ReactNode;
  onDismiss?: () => void;
  className?: string;
}
