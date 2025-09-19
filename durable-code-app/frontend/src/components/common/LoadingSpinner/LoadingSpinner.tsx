import React from 'react';
import styles from './LoadingSpinner.module.css';
import type { LoadingSpinnerProps } from './LoadingSpinner.types';

export const LoadingSpinner = React.memo<LoadingSpinnerProps>(
  ({
    size = 'medium',
    variant = 'primary',
    className = '',
    label = 'Loading...',
    ...rest
  }) => {
    const classNames = [styles.spinner, styles[size], styles[variant], className]
      .filter(Boolean)
      .join(' ');

    return (
      <div className={classNames} role="status" aria-label={label} {...rest}>
        <div className={styles.circle} />
        <span className={styles.visuallyHidden}>{label}</span>
      </div>
    );
  },
);

LoadingSpinner.displayName = 'LoadingSpinner';
