import React from 'react';
import styles from './Badge.module.css';
import type { BadgeProps } from './Badge.types';

export const Badge = React.memo<BadgeProps>(
  ({ children, variant = 'neutral', size = 'medium', className = '', ...rest }) => {
    const classNames = [styles.badge, styles[variant], styles[size], className]
      .filter(Boolean)
      .join(' ');

    return (
      <span className={classNames} {...rest}>
        {children}
      </span>
    );
  },
);

Badge.displayName = 'Badge';
