/**
 * Purpose: Constants and configuration values for the oscilloscope demo feature
 * Scope: Application constants, default values, and configuration parameters
 * Overview: Centralized constants for oscilloscope behavior including default state,
 *     WebSocket configuration, canvas settings, and UI parameters.
 * Dependencies: None
 * Exports: DEFAULT_OSCILLOSCOPE_STATE, WEBSOCKET_CONFIG, CANVAS_CONFIG, UI_CONFIG
 * Interfaces: Configuration objects and constant values
 * Implementation: Static configuration values used throughout the demo feature
 */

import type { OscilloscopeState } from '../types/oscilloscope.types';

export const DEFAULT_OSCILLOSCOPE_STATE: OscilloscopeState = {
  isConnected: false,
  isStreaming: false,
  waveType: 'sine',
  frequency: 10,
  amplitude: 1,
  offset: 0,
  zoom: 1,
  timeScale: 10, // ms/div
  voltScale: 1, // V/div
  triggerLevel: 0,
  isPaused: false,
};

export const WEBSOCKET_CONFIG = {
  BACKEND_PORT: 8000,
  ENDPOINT: '/api/oscilloscope/stream',
  RECONNECT_DELAY: 3000,
  MAX_RECONNECT_ATTEMPTS: 5,
} as const;

export const CANVAS_CONFIG = {
  DEFAULT_WIDTH: 800,
  DEFAULT_HEIGHT: 400,
  BACKGROUND_COLOR: '#1a1a1a',
  GRID_COLOR: '#2a2a2a',
  CENTER_LINE_COLOR: '#3a3a3a',
  WAVEFORM_COLOR: '#00ff00',
  TRIGGER_COLOR: '#ff9900',
  TEXT_COLOR: '#00ff00',
  BORDER_COLOR: '#333',
  BORDER_RADIUS: '8px',
  GRID_DIVISIONS_HORIZONTAL: 10,
  GRID_DIVISIONS_VERTICAL: 8,
} as const;

export const DATA_CONFIG = {
  MAX_BUFFER_SIZE: 2000,
  DEFAULT_SAMPLE_RATE: 1000, // samples per second
  FPS_CALCULATION_INTERVAL: 1000, // ms
} as const;

export const PARAMETER_LIMITS = {
  FREQUENCY: { min: 0.1, max: 100, step: 0.1 },
  AMPLITUDE: { min: 0.1, max: 10, step: 0.1 },
  OFFSET: { min: -10, max: 10, step: 0.1 },
  TIME_SCALE: { min: 1, max: 100, step: 1 },
  VOLT_SCALE: { min: 0.1, max: 10, step: 0.1 },
  TRIGGER_LEVEL: { min: -5, max: 5, step: 0.1 },
} as const;

export const UI_CONFIG = {
  CONTROL_PANEL_GAP: '10px',
  CONTROL_GROUP_GAP: '15px',
  BUTTON_PADDING: '10px 20px',
  CONTROL_GRID_MIN_WIDTH: '200px',
  STATUS_PANEL_PADDING: '10px',
  STATUS_PANEL_BACKGROUND: '#2a2a2a',
} as const;
