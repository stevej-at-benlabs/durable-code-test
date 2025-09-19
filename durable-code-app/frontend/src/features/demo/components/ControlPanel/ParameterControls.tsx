/**
 * Purpose: Parameter control sliders component for oscilloscope settings
 * Scope: UI component for adjusting oscilloscope parameters via sliders
 * Overview: Provides a comprehensive set of sliders for controlling oscilloscope
 *     parameters including frequency, amplitude, time scale, voltage scale,
 *     trigger level, and DC offset with proper labeling and value display.
 * Dependencies: React, oscilloscope types and constants
 * Exports: ParameterControls component
 * Interfaces: Props interface for parameter control callbacks
 * Implementation: Grid-based layout with labeled range inputs and value displays
 */

import React from 'react';
import type { OscilloscopeState } from '../../types/oscilloscope.types';
import { PARAMETER_LIMITS } from '../../constants/oscilloscope.constants';
import styles from './ParameterControls.module.css';

interface ParameterControlsProps {
  state: Pick<
    OscilloscopeState,
    'frequency' | 'amplitude' | 'offset' | 'timeScale' | 'voltScale' | 'triggerLevel'
  >;
  onFrequencyChange: (value: number) => void;
  onAmplitudeChange: (value: number) => void;
  onOffsetChange: (value: number) => void;
  onTimeScaleChange: (value: number) => void;
  onVoltScaleChange: (value: number) => void;
  onTriggerLevelChange: (value: number) => void;
  disabled?: boolean;
}

interface ControlConfig {
  key: keyof Pick<
    OscilloscopeState,
    'frequency' | 'amplitude' | 'offset' | 'timeScale' | 'voltScale' | 'triggerLevel'
  >;
  label: string;
  unit: string;
  limits: { min: number; max: number; step: number };
  onChange: (value: number) => void;
  precision?: number;
}

export const ParameterControls: React.FC<ParameterControlsProps> = ({
  state,
  onFrequencyChange,
  onAmplitudeChange,
  onOffsetChange,
  onTimeScaleChange,
  onVoltScaleChange,
  onTriggerLevelChange,
  disabled = false,
}) => {
  const controls: ControlConfig[] = [
    {
      key: 'frequency',
      label: 'Frequency',
      unit: 'Hz',
      limits: PARAMETER_LIMITS.FREQUENCY,
      onChange: onFrequencyChange,
      precision: 1,
    },
    {
      key: 'amplitude',
      label: 'Amplitude',
      unit: '',
      limits: PARAMETER_LIMITS.AMPLITUDE,
      onChange: onAmplitudeChange,
      precision: 1,
    },
    {
      key: 'timeScale',
      label: 'Time Scale',
      unit: 'ms/div',
      limits: PARAMETER_LIMITS.TIME_SCALE,
      onChange: onTimeScaleChange,
      precision: 0,
    },
    {
      key: 'voltScale',
      label: 'Voltage Scale',
      unit: 'V/div',
      limits: PARAMETER_LIMITS.VOLT_SCALE,
      onChange: onVoltScaleChange,
      precision: 1,
    },
    {
      key: 'triggerLevel',
      label: 'Trigger Level',
      unit: '',
      limits: PARAMETER_LIMITS.TRIGGER_LEVEL,
      onChange: onTriggerLevelChange,
      precision: 1,
    },
    {
      key: 'offset',
      label: 'DC Offset',
      unit: '',
      limits: PARAMETER_LIMITS.OFFSET,
      onChange: onOffsetChange,
      precision: 1,
    },
  ];

  const formatValue = (value: number, precision: number = 1): string => {
    return precision === 0 ? value.toString() : value.toFixed(precision);
  };

  return (
    <div className={styles.container}>
      {controls.map(({ key, label, unit, limits, onChange, precision = 1 }) => (
        <div key={key} className={styles.controlGroup}>
          <label className={styles.label}>
            {label} ({unit}): {formatValue(state[key], precision)}
          </label>
          <input
            type="range"
            min={limits.min}
            max={limits.max}
            step={limits.step}
            value={state[key]}
            onChange={(e) => onChange(parseFloat(e.target.value))}
            disabled={disabled}
            className={styles.slider}
          />
        </div>
      ))}
    </div>
  );
};
