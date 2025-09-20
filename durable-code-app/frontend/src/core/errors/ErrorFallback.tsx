/**
 * Purpose: Fallback UI component for error boundaries
 * Scope: User-friendly error display with recovery options
 * Overview: Displays error information and provides recovery actions
 * Dependencies: React, error types, styles
 * Exports: ErrorFallback component
 * Props/Interfaces: ErrorFallbackProps
 * Implementation: Accessible, informative error UI with multiple recovery paths
 */

import { useState, useCallback } from 'react';
import type { ReactElement } from 'react';
import type { ErrorFallbackProps } from './ErrorBoundary.types';
import styles from './ErrorFallback.module.css';

export function ErrorFallback({
  error,
  errorInfo,
  onReset,
  onRetry,
  onHome,
  level = 'component',
  name,
  retryCount = 0,
  maxRetries = 3,
}: ErrorFallbackProps): ReactElement {
  const [showDetails, setShowDetails] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = useCallback(async () => {
    if (onRetry && retryCount < maxRetries) {
      setIsRetrying(true);
      try {
        await new Promise((resolve) => setTimeout(resolve, 500)); // Brief delay for UX
        onRetry();
      } finally {
        setIsRetrying(false);
      }
    }
  }, [onRetry, retryCount, maxRetries]);

  const handleHome = useCallback(() => {
    if (onHome) {
      onHome();
    } else {
      window.location.href = '/';
    }
  }, [onHome]);

  const getErrorIcon = () => {
    switch (level) {
      case 'page':
        return '🚨';
      case 'feature':
        return '⚠️';
      case 'component':
      default:
        return '❌';
    }
  };

  const getErrorTitle = () => {
    switch (level) {
      case 'page':
        return 'Page Error';
      case 'feature':
        return 'Feature Error';
      case 'component':
      default:
        return 'Component Error';
    }
  };

  const getErrorMessage = () => {
    const location = name ? ` in ${name}` : '';

    switch (level) {
      case 'page':
        return `The page${location} encountered an error and cannot be displayed. You can try refreshing the page or returning home.`;
      case 'feature':
        return `The feature${location} is temporarily unavailable. You can try again or continue with other features.`;
      case 'component':
      default:
        return `A component${location} failed to render properly. The error has been logged and you can try refreshing.`;
    }
  };

  const containerClass = `${styles.errorContainer} ${styles[`errorContainer${level.charAt(0).toUpperCase() + level.slice(1)}`]}`;

  return (
    <div className={containerClass} role="alert" aria-live="assertive">
      <div className={styles.errorContent}>
        <div className={styles.errorIcon} aria-hidden="true">
          {getErrorIcon()}
        </div>

        <h2 className={styles.errorTitle}>{getErrorTitle()}</h2>

        <p className={styles.errorMessage}>{getErrorMessage()}</p>

        {retryCount > 0 && (
          <div className={styles.retryIndicator}>
            <span>⚡</span>
            <span>
              Retry attempt <span className={styles.retryCount}>{retryCount}</span> of{' '}
              {maxRetries}
            </span>
          </div>
        )}

        {process.env.NODE_ENV === 'development' && (
          <div className={styles.errorDetails}>
            <button
              className={styles.errorDetailsToggle}
              onClick={() => setShowDetails(!showDetails)}
              aria-expanded={showDetails}
            >
              {showDetails ? 'Hide' : 'Show'} Error Details
            </button>

            {showDetails && (
              <>
                <div>
                  <strong>Error:</strong> {error.message}
                </div>
                {error.stack && (
                  <pre className={styles.errorStack}>{error.stack}</pre>
                )}
                {errorInfo?.componentStack && (
                  <div>
                    <strong>Component Stack:</strong>
                    <pre className={styles.errorStack}>
                      {errorInfo.componentStack}
                    </pre>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        <div className={styles.errorActions}>
          {onRetry && retryCount < maxRetries && (
            <button
              className={`${styles.errorButton} ${styles.errorButtonPrimary}`}
              onClick={handleRetry}
              disabled={isRetrying}
              aria-busy={isRetrying}
            >
              {isRetrying ? (
                <>
                  <span>⏳</span> Retrying...
                </>
              ) : (
                <>
                  <span>🔄</span> Try Again
                </>
              )}
            </button>
          )}

          <button
            className={`${styles.errorButton} ${styles.errorButtonSecondary}`}
            onClick={onReset}
          >
            <span>♻️</span> Reset
          </button>

          <button
            className={`${styles.errorButton} ${styles.errorButtonSecondary}`}
            onClick={handleHome}
          >
            <span>🏠</span> Go Home
          </button>
        </div>

        <div className={styles.errorMeta}>
          <div className={styles.errorMetaItem}>
            <strong>Time:</strong> {new Date().toLocaleString()}
          </div>
          {errorInfo?.digest && (
            <div className={styles.errorMetaItem}>
              <strong>Error ID:</strong> {errorInfo.digest}
            </div>
          )}
          {process.env.NODE_ENV === 'development' && (
            <div className={styles.errorMetaItem}>
              <strong>Environment:</strong> Development
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ErrorFallback;