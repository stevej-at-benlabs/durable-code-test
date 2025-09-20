/**
 * Purpose: Type definitions for error boundary components
 * Scope: Type safety for error handling infrastructure
 * Overview: Interfaces and types for error boundaries, recovery, and logging
 * Dependencies: React types
 * Exports: All error boundary related types
 * Interfaces: ErrorInfo, ErrorBoundaryState, ErrorBoundaryProps, ErrorRecoveryOptions
 * Implementation: Comprehensive type definitions for robust error handling
 */

import type { ErrorInfo as ReactErrorInfo, ReactNode } from 'react';

/**
 * Error information with additional context
 */
export interface ErrorInfo extends ReactErrorInfo {
  digest?: string;
  timestamp: number;
  userAgent: string;
  url: string;
  errorBoundary?: string;
  errorBoundaryProps?: Record<string, unknown>;
}

/**
 * Error boundary component state
 */
export interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorCount: number;
  lastErrorTime: number | null;
}

/**
 * Error recovery action types
 */
export type ErrorRecoveryAction = 'retry' | 'reload' | 'home' | 'reset';

/**
 * Error recovery options
 */
export interface ErrorRecoveryOptions {
  onRetry?: () => void;
  onReset?: () => void;
  maxRetries?: number;
  retryDelay?: number;
  enableAutoRecovery?: boolean;
  autoRecoveryDelay?: number;
}

/**
 * Error boundary component props
 */
export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  resetKeys?: Array<string | number>;
  resetOnPropsChange?: boolean;
  isolate?: boolean;
  level?: 'page' | 'feature' | 'component';
  name?: string;
  recoveryOptions?: ErrorRecoveryOptions;
}

/**
 * Error fallback component props
 */
export interface ErrorFallbackProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  onReset: () => void;
  onRetry?: () => void;
  onHome?: () => void;
  level?: 'page' | 'feature' | 'component';
  name?: string;
  retryCount?: number;
  maxRetries?: number;
}

/**
 * Error logger interface
 */
export interface ErrorLogger {
  logError: (error: Error, errorInfo: ErrorInfo) => void;
  logRecovery: (action: ErrorRecoveryAction, success: boolean) => void;
  logWarning: (message: string, context?: Record<string, unknown>) => void;
}

/**
 * Global error handler options
 */
export interface GlobalErrorHandlerOptions {
  onUnhandledRejection?: (event: PromiseRejectionEvent) => void;
  onError?: (event: ErrorEvent) => void;
  logToConsole?: boolean;
  logToService?: boolean;
  serviceUrl?: string;
}
