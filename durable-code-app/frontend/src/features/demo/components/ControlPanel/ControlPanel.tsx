/**
 * Purpose: Main control panel component for oscilloscope demo interface
 * Scope: Composite component containing all oscilloscope controls and actions
 * Overview: Provides a comprehensive control interface for the oscilloscope demo
 *     including streaming controls, waveform selection, parameter adjustments,
 *     and utility functions like pause and clear buffer.
 * Dependencies: React, Button component, child control components, oscilloscope types
 * Exports: ControlPanel component
 * Interfaces: Props interface for control panel callbacks and state
 * Implementation: Composite component organizing all control sub-components
 */

import React from 'react';
import { Button } from '../../../../components/common/Button';
import { WaveformSelector } from './WaveformSelector';
import { ParameterControls } from './ParameterControls';
import type { ControlPanelProps } from '../../types/oscilloscope.types';
import styles from './ControlPanel.module.css';

export const ControlPanel: React.FC<ControlPanelProps> = ({
  state,
  onStateChange,
  onStartStreaming,
  onStopStreaming,
  onClearBuffer,
  onUpdateWaveform,
  onFrequencyChange,
  onAmplitudeChange,
  onOffsetChange,
}) => {
  const handlePauseToggle = () => {
    onStateChange({ isPaused: !state.isPaused });
  };

  const handleTimeScaleChange = (timeScale: number) => {
    onStateChange({ timeScale });
  };

  const handleVoltScaleChange = (voltScale: number) => {
    onStateChange({ voltScale });
  };

  const handleTriggerLevelChange = (triggerLevel: number) => {
    onStateChange({ triggerLevel });
  };

  return (
    <div className={styles.container}>
      {/* Streaming Controls */}
      <div className={styles.controlRow}>
        <Button
          onClick={onStartStreaming}
          disabled={!state.isConnected || state.isStreaming}
          variant="primary"
          size="medium"
        >
          ▶ Start
        </Button>
        <Button
          onClick={onStopStreaming}
          disabled={!state.isConnected || !state.isStreaming}
          variant="danger"
          size="medium"
        >
          ⏹ Stop
        </Button>
        <button
          onClick={handlePauseToggle}
          className={`${styles.controlButton} ${state.isPaused ? styles.paused : ''}`}
          disabled={!state.isConnected}
        >
          {state.isPaused ? '⏸ Paused' : '⏸ Pause'}
        </button>
        <button
          onClick={onClearBuffer}
          className={styles.controlButton}
          disabled={!state.isConnected}
        >
          🗑️ Clear
        </button>
      </div>

      {/* Waveform Selection */}
      <WaveformSelector
        selectedWaveType={state.waveType}
        onWaveTypeChange={onUpdateWaveform}
        disabled={!state.isConnected}
      />

      {/* Parameter Controls */}
      <ParameterControls
        state={state}
        onFrequencyChange={onFrequencyChange}
        onAmplitudeChange={onAmplitudeChange}
        onOffsetChange={onOffsetChange}
        onTimeScaleChange={handleTimeScaleChange}
        onVoltScaleChange={handleVoltScaleChange}
        onTriggerLevelChange={handleTriggerLevelChange}
        disabled={!state.isConnected}
      />
    </div>
  );
};
