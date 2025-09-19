/**
 * Purpose: Waveform type selection component for oscilloscope controls
 * Scope: UI component for selecting waveform types (sine, square, noise)
 * Overview: Provides a clean interface for selecting different waveform types
 *     with visual indicators and proper styling. Supports sine waves, square waves,
 *     and white noise generation options.
 * Dependencies: React, Button component, oscilloscope types
 * Exports: WaveformSelector component
 * Interfaces: Props interface for waveform selection
 * Implementation: Button-based selector with active state styling
 */

import React from 'react';
import type { WaveType } from '../../types/oscilloscope.types';
import styles from './WaveformSelector.module.css';

interface WaveformSelectorProps {
  selectedWaveType: WaveType;
  onWaveTypeChange: (waveType: WaveType) => void;
  disabled?: boolean;
}

const WAVEFORM_OPTIONS = [
  { type: 'sine' as const, label: '∿ Sine Wave', symbol: '∿' },
  { type: 'square' as const, label: '⊓ Square Wave', symbol: '⊓' },
  { type: 'noise' as const, label: '≋ White Noise', symbol: '≋' },
];

export const WaveformSelector: React.FC<WaveformSelectorProps> = ({
  selectedWaveType,
  onWaveTypeChange,
  disabled = false,
}) => {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>Waveform Type</h3>
      <div className={styles.buttonGroup}>
        {WAVEFORM_OPTIONS.map(({ type, label }) => (
          <button
            key={type}
            onClick={() => onWaveTypeChange(type)}
            disabled={disabled}
            className={`${styles.waveformButton} ${
              selectedWaveType === type ? styles.active : ''
            }`}
            aria-pressed={selectedWaveType === type}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
};
