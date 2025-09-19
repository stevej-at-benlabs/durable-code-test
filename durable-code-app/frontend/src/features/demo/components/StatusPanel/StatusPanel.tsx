/**
 * Purpose: Status panel component for displaying oscilloscope connection and data metrics
 * Scope: UI component for showing connection status, streaming state, and performance metrics
 * Overview: Provides real-time status information for the oscilloscope demo including
 *     WebSocket connection state, streaming status, data rate, buffer size, and FPS.
 *     Features visual indicators for quick status recognition.
 * Dependencies: React, oscilloscope types and constants
 * Exports: StatusPanel component
 * Interfaces: Props interface for status data
 * Implementation: Clean status display with color-coded indicators and performance metrics
 */

import React from 'react';
import type { StatusPanelProps } from '../../types/oscilloscope.types';
import styles from './StatusPanel.module.css';

export const StatusPanel: React.FC<StatusPanelProps> = ({ state, stats }) => {
  const getConnectionStatusColor = (isConnected: boolean): string => {
    return isConnected ? '#00ff00' : '#ff4444';
  };

  const getStreamingStatusColor = (isStreaming: boolean): string => {
    return isStreaming ? '#00ff00' : '#666';
  };

  const formatDataRate = (rate: number): string => {
    if (rate >= 1000) {
      return `${(rate / 1000).toFixed(1)}k S/s`;
    }
    return `${rate} S/s`;
  };

  const formatBufferSize = (size: number): string => {
    return `${size.toLocaleString()} samples`;
  };

  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Connection Status</h3>
      <div className={styles.statusGrid}>
        <div className={styles.statusItem}>
          <span className={styles.label}>Connection:</span>
          <span
            className={styles.value}
            style={{ color: getConnectionStatusColor(state.isConnected) }}
          >
            {state.isConnected ? '● Connected' : '○ Disconnected'}
          </span>
        </div>

        <div className={styles.statusItem}>
          <span className={styles.label}>Streaming:</span>
          <span
            className={styles.value}
            style={{ color: getStreamingStatusColor(state.isStreaming) }}
          >
            {state.isStreaming ? '● Active' : '○ Inactive'}
          </span>
        </div>

        <div className={styles.statusItem}>
          <span className={styles.label}>Data Rate:</span>
          <span className={styles.value}>{formatDataRate(stats.dataRate)}</span>
        </div>

        <div className={styles.statusItem}>
          <span className={styles.label}>Buffer:</span>
          <span className={styles.value}>{formatBufferSize(stats.bufferSize)}</span>
        </div>

        <div className={styles.statusItem}>
          <span className={styles.label}>FPS:</span>
          <span className={styles.value}>{stats.fps}</span>
        </div>

        <div className={styles.statusItem}>
          <span className={styles.label}>Performance:</span>
          <span
            className={`${styles.value} ${styles.performance}`}
            style={{
              color:
                stats.fps >= 30 ? '#00ff00' : stats.fps >= 15 ? '#ffa500' : '#ff4444',
            }}
          >
            {stats.fps >= 30 ? 'Excellent' : stats.fps >= 15 ? 'Good' : 'Poor'}
          </span>
        </div>
      </div>
    </div>
  );
};
