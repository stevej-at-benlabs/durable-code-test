/**
 * Purpose: Central export for error handling infrastructure
 * Scope: Error boundaries, logging, and global handlers
 * Overview: Exports all error handling components and utilities
 * Dependencies: All error handling modules
 * Exports: All error handling components, types, and utilities
 * Implementation: Barrel export for convenient imports
 */

// Components
export { ErrorBoundary } from './ErrorBoundary';
export { ErrorFallback } from './ErrorFallback';

// Services
export { ErrorLogger, errorLogger } from './ErrorLogger';
export {
  GlobalErrorHandler,
  setupGlobalErrorHandling,
  teardownGlobalErrorHandling,
} from './GlobalErrorHandler';

// Types
export type {
  ErrorInfo,
  ErrorBoundaryState,
  ErrorBoundaryProps,
  ErrorFallbackProps,
  ErrorRecoveryAction,
  ErrorRecoveryOptions,
  GlobalErrorHandlerOptions,
} from './ErrorBoundary.types';
