/**
 * Purpose: Performance monitoring module exports
 * Scope: Central export point for performance monitoring infrastructure
 * Overview: Provides a unified interface to all performance monitoring
 *     utilities, including the main monitor class, React hooks, and types.
 * Dependencies: Performance monitor and hooks
 * Exports: All performance monitoring utilities
 * Interfaces: Re-exports all performance types
 * Implementation: Simple module aggregation with clean exports
 */

export { PerformanceMonitor } from './PerformanceMonitor';
export { usePerformanceMetrics } from './usePerformanceMetrics';
export type {
  PerformanceMetrics,
  PerformanceAlert,
  PerformanceThresholds,
} from './PerformanceMonitor';
