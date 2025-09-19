import type { HTMLAttributes, ReactNode } from 'react';

export type SectionVariant = 'default' | 'highlighted' | 'bordered';

export interface SectionProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  title?: string;
  variant?: SectionVariant;
  className?: string;
}
