/**
 * Purpose: Main demo tab feature component for oscilloscope demonstration
 * Scope: Complete oscilloscope demo feature integrating all sub-components
 * Overview: Provides the complete oscilloscope demonstration interface by integrating
 *     canvas visualization, control panels, status display, and documentation sections.
 *     Uses custom hooks for state management and WebSocket communication.
 * Dependencies: React, oscilloscope hook, child components
 * Exports: DemoTab component
 * Interfaces: Self-contained tab component with no external props
 * Implementation: Feature-based architecture with modular components and hooks
 */

import { useCallback } from 'react';
import type { ReactElement } from 'react';
import { useOscilloscope } from '../../hooks/useOscilloscope';
import { OscilloscopeCanvas } from '../Oscilloscope';
import { ControlPanel } from '../ControlPanel';
import { StatusPanel } from '../StatusPanel';
import { DetailsCard } from '../../../../components/common';
import styles from './DemoTab.module.css';

export function DemoTab(): ReactElement {
  const {
    state,
    stats,
    dataBuffer,
    startStreaming,
    stopStreaming,
    updateWaveform,
    updateFrequency,
    updateAmplitude,
    updateOffset,
    updateTimeScale,
    updateVoltScale,
    updateTriggerLevel,
    togglePause,
    clearBuffer,
    resetToDefaults,
    error,
  } = useOscilloscope();

  const handleStateChange = useCallback(
    (newState: Partial<typeof state>) => {
      // Handle state changes that don't have specific handlers
      if (newState.isPaused !== undefined) {
        togglePause();
      }
      if (newState.timeScale !== undefined) {
        updateTimeScale(newState.timeScale);
      }
      if (newState.voltScale !== undefined) {
        updateVoltScale(newState.voltScale);
      }
      if (newState.triggerLevel !== undefined) {
        updateTriggerLevel(newState.triggerLevel);
      }
    },
    [togglePause, updateTimeScale, updateVoltScale, updateTriggerLevel],
  );

  return (
    <div className="tab-content demo-content">
      {/* Hero Section */}
      <div className={styles.demoHero}>
        <h3 className={styles.demoTitle}>
          <span className={styles.titleIcon}>🎭</span>
          Oscilloscope Demo
        </h3>
        <p className={styles.demoSubtitle}>
          Built entirely by AI while the human went to dinner! Less than 10 minutes to
          build, followed by 15 minutes of human review. Fully linted and tested.
        </p>
      </div>

      {/* Error Display */}
      {error && (
        <div className={styles.errorContainer}>
          <div className={styles.errorMessage}>
            <span className={styles.errorIcon}>⚠️</span>
            <span>Connection Error: {error.message}</span>
          </div>
        </div>
      )}

      {/* Main Demo Showcase */}
      <div className={styles.demoShowcase}>
        <div className={styles.showcaseContainer}>
          {/* Oscilloscope Display */}
          <div className={styles.oscilloscopeContainer}>
            <OscilloscopeCanvas data={dataBuffer} state={state} stats={stats} />
          </div>

          {/* Control Panel */}
          <ControlPanel
            state={state}
            onStateChange={handleStateChange}
            onStartStreaming={startStreaming}
            onStopStreaming={stopStreaming}
            onClearBuffer={clearBuffer}
            onUpdateWaveform={updateWaveform}
            onFrequencyChange={updateFrequency}
            onAmplitudeChange={updateAmplitude}
            onOffsetChange={updateOffset}
            onReset={resetToDefaults}
          />

          {/* Status Panel */}
          <StatusPanel state={state} stats={stats} />
        </div>
      </div>

      {/* Documentation Section */}
      <DetailsCard title="About This Demo" icon="📖">
        <p>
          This interactive oscilloscope demonstrates real-time data streaming using
          WebSockets and canvas-based visualization. The backend generates waveforms in
          real-time and streams them to the frontend for display.
        </p>

        <h3>Features</h3>
        <ul>
          <li>Real-time WebSocket streaming</li>
          <li>Multiple waveform types (sine, square, white noise)</li>
          <li>Adjustable frequency, amplitude, and offset</li>
          <li>Zoom and scale controls</li>
          <li>Trigger level adjustment</li>
          <li>Pause and clear functionality</li>
          <li>Performance monitoring (FPS, data rate)</li>
        </ul>

        <h3>Technical Implementation</h3>
        <ul>
          <li>Backend: FastAPI with WebSocket support</li>
          <li>Frontend: React with Canvas API</li>
          <li>Protocol: JSON over WebSocket</li>
          <li>Visualization: Hardware-accelerated canvas rendering</li>
        </ul>
      </DetailsCard>

      {/* Footer */}
      <DetailsCard title="Demo Summary" icon="⚡">
        <p>
          This oscilloscope demo showcases real-time data streaming and visualization
          capabilities of the durable code framework.
        </p>
      </DetailsCard>
    </div>
  );
}
