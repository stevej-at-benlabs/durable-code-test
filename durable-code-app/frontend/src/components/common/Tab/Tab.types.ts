import type { ButtonHTMLAttributes, ReactNode } from 'react';

export type TabVariant = 'default' | 'underline' | 'pill';

export interface TabProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  isActive?: boolean;
  variant?: TabVariant;
  className?: string;
}
