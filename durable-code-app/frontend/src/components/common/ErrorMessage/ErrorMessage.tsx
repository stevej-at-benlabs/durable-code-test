import React from 'react';
import styles from './ErrorMessage.module.css';
import type { ErrorMessageProps } from './ErrorMessage.types';

export const ErrorMessage = React.memo<ErrorMessageProps>(
  ({
    message,
    title,
    variant = 'error',
    children,
    onDismiss,
    className = '',
    ...rest
  }) => {
    const classNames = [styles.errorMessage, styles[variant], className]
      .filter(Boolean)
      .join(' ');

    const getIcon = () => {
      switch (variant) {
        case 'error':
          return '❌';
        case 'warning':
          return '⚠️';
        case 'info':
          return 'ℹ️';
        default:
          return '❌';
      }
    };

    return (
      <div className={classNames} role="alert" aria-live="polite" {...rest}>
        <div className={styles.content}>
          <div className={styles.header}>
            <span className={styles.icon} role="img" aria-hidden="true">
              {getIcon()}
            </span>
            {title && <h4 className={styles.title}>{title}</h4>}
            {onDismiss && (
              <button
                className={styles.dismissButton}
                onClick={onDismiss}
                aria-label="Dismiss message"
                type="button"
              >
                ✕
              </button>
            )}
          </div>
          <div className={styles.message}>{message}</div>
          {children && <div className={styles.children}>{children}</div>}
        </div>
      </div>
    );
  },
);

ErrorMessage.displayName = 'ErrorMessage';
