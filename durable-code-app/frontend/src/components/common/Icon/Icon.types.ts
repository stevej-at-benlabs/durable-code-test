import type { HTMLAttributes } from 'react';

export type IconSize = 'small' | 'medium' | 'large' | 'xl';

export interface IconProps extends HTMLAttributes<HTMLSpanElement> {
  emoji: string;
  label: string;
  size?: IconSize;
  className?: string;
}
