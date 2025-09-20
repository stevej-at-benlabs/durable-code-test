/**
 * Purpose: React hook for performance monitoring integration
 * Scope: Hook interface for performance monitoring in React components
 * Overview: Provides a React hook that integrates with the PerformanceMonitor
 *     singleton to track component performance, render times, and provide
 *     real-time performance feedback to components.
 * Dependencies: React hooks, PerformanceMonitor
 * Exports: usePerformanceMetrics hook
 * Interfaces: Hook return type with metrics and control methods
 * Implementation: React hook wrapper around PerformanceMonitor with lifecycle management
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { PerformanceMonitor } from './PerformanceMonitor';
import type { PerformanceAlert, PerformanceMetrics } from './PerformanceMonitor';

interface UsePerformanceMetricsOptions {
  componentName?: string;
  trackRenders?: boolean;
  alertsEnabled?: boolean;
}

interface UsePerformanceMetricsReturn {
  metrics: PerformanceMetrics | null;
  alerts: PerformanceAlert[];
  recordRender: (renderTime?: number) => void;
  startMeasuring: () => () => void;
  isMonitoring: boolean;
  summary: {
    avgFps: number;
    avgRenderTime: number;
    avgMemory: number;
    alerts: number;
  };
}

export function usePerformanceMetrics(
  options: UsePerformanceMetricsOptions = {},
): UsePerformanceMetricsReturn {
  const {
    componentName = 'UnknownComponent',
    trackRenders = true,
    alertsEnabled = true,
  } = options;

  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(false);

  const monitor = useRef<PerformanceMonitor>(PerformanceMonitor.getInstance());
  const renderStartTime = useRef<number>(0);
  const alertCleanup = useRef<(() => void) | null>(null);

  // Setup performance monitoring
  useEffect(() => {
    const performanceMonitor = monitor.current;

    // Start monitoring
    performanceMonitor.startMonitoring();
    setIsMonitoring(true);

    // Setup alert handler if enabled
    if (alertsEnabled) {
      alertCleanup.current = performanceMonitor.onPerformanceAlert((alert) => {
        setAlerts((prev) => [...prev.slice(-9), alert]); // Keep last 10 alerts
      });
    }

    // Update metrics periodically
    const metricsInterval = setInterval(() => {
      setMetrics(performanceMonitor.getCurrentMetrics());
    }, 1000);

    // Cleanup
    return () => {
      clearInterval(metricsInterval);
      if (alertCleanup.current) {
        alertCleanup.current();
        alertCleanup.current = null;
      }
      performanceMonitor.stopMonitoring();
      setIsMonitoring(false);
    };
  }, [alertsEnabled]);

  // Record render performance
  const recordRender = useCallback(
    (renderTime?: number) => {
      if (!trackRenders) return;

      const actualRenderTime =
        renderTime ?? performance.now() - renderStartTime.current;
      monitor.current.recordMetric(componentName, actualRenderTime);
    },
    [componentName, trackRenders],
  );

  // Start measuring render time
  const startMeasuring = useCallback(() => {
    renderStartTime.current = performance.now();

    // Return stop function
    return () => {
      const renderTime = performance.now() - renderStartTime.current;
      recordRender(renderTime);
    };
  }, [recordRender]);

  // Get performance summary
  const summary = monitor.current.getPerformanceSummary();

  return {
    metrics,
    alerts,
    recordRender,
    startMeasuring,
    isMonitoring,
    summary,
  };
}
