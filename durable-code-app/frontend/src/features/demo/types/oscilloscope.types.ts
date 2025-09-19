/**
 * Purpose: TypeScript type definitions for the oscilloscope demo feature
 * Scope: Interfaces and types for oscilloscope state, data, and configuration
 * Overview: Defines the data structures used throughout the demo feature including
 *     oscilloscope state management, WebSocket data formats, and component props.
 * Dependencies: None (base TypeScript types only)
 * Exports: OscilloscopeState, OscilloscopeData, WebSocketCommand, OscilloscopeStats
 * Interfaces: State management, data transfer, and component interfaces
 * Implementation: Pure TypeScript type definitions for type safety
 */

export type WaveType = 'sine' | 'square' | 'noise';

export interface OscilloscopeState {
  isConnected: boolean;
  isStreaming: boolean;
  waveType: WaveType;
  frequency: number;
  amplitude: number;
  offset: number;
  zoom: number;
  timeScale: number;
  voltScale: number;
  triggerLevel: number;
  isPaused: boolean;
}

export interface OscilloscopeData {
  timestamp: number;
  samples: number[];
  sample_rate: number;
  wave_type: string;
  parameters: {
    frequency: number;
    amplitude: number;
    offset: number;
  };
}

export interface OscilloscopeStats {
  fps: number;
  dataRate: number;
  bufferSize: number;
}

export interface WebSocketCommand {
  command: 'start' | 'stop' | 'configure';
  wave_type?: WaveType;
  frequency?: number;
  amplitude?: number;
  offset?: number;
}

export interface CanvasDrawProps {
  width: number;
  height: number;
  data: number[];
  state: Pick<
    OscilloscopeState,
    'timeScale' | 'voltScale' | 'triggerLevel' | 'isPaused'
  >;
  stats: OscilloscopeStats;
}

export interface ControlPanelProps {
  state: OscilloscopeState;
  onStateChange: (newState: Partial<OscilloscopeState>) => void;
  onStartStreaming: () => void;
  onStopStreaming: () => void;
  onClearBuffer: () => void;
  onUpdateWaveform: (waveType: WaveType) => void;
  onFrequencyChange: (frequency: number) => void;
  onAmplitudeChange: (amplitude: number) => void;
  onOffsetChange: (offset: number) => void;
  onReset?: () => void;
}

export interface StatusPanelProps {
  state: Pick<OscilloscopeState, 'isConnected' | 'isStreaming'>;
  stats: OscilloscopeStats;
}

export interface OscilloscopeCanvasProps {
  data: number[];
  state: Pick<
    OscilloscopeState,
    'timeScale' | 'voltScale' | 'triggerLevel' | 'isPaused' | 'frequency'
  >;
  stats: OscilloscopeStats;
}
