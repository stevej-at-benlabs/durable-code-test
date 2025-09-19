import React from 'react';
import styles from './Button.module.css';
import type { ButtonProps } from './Button.types';

export const Button = React.memo<ButtonProps>(
  ({
    children,
    variant = 'primary',
    size = 'medium',
    isLoading = false,
    fullWidth = false,
    disabled = false,
    className = '',
    ...rest
  }) => {
    const classNames = [
      styles.button,
      styles[variant],
      styles[size],
      fullWidth && styles.fullWidth,
      isLoading && styles.loading,
      className,
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <button className={classNames} disabled={disabled || isLoading} {...rest}>
        {isLoading && <span className={styles.spinner} />}
        {children}
      </button>
    );
  },
);

Button.displayName = 'Button';
