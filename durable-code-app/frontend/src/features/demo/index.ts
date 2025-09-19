/**
 * Purpose: Barrel export for demo feature module
 * Scope: Feature exports for the oscilloscope demo
 * Overview: Provides clean import interface for the complete demo feature including
 *     main component, hooks, services, and types.
 * Dependencies: All demo feature components and utilities
 * Exports: DemoTab (primary), hooks, services, types
 * Implementation: Comprehensive feature export for external consumption
 */

// Main component
export { DemoTab } from './components/DemoTab';

// Sub-components (for potential reuse)
export { OscilloscopeCanvas } from './components/Oscilloscope';
export {
  ControlPanel,
  WaveformSelector,
  ParameterControls,
} from './components/ControlPanel';
export { StatusPanel } from './components/StatusPanel';

// Hooks
export { useWebSocket } from './hooks/useWebSocket';
export { useOscilloscope } from './hooks/useOscilloscope';
export { useCanvas } from './hooks/useCanvas';

// Services
export { WebSocketService } from './services/websocketService';

// Types
export type {
  OscilloscopeState,
  OscilloscopeData,
  OscilloscopeStats,
  WebSocketCommand,
  WaveType,
  ControlPanelProps,
  StatusPanelProps,
  OscilloscopeCanvasProps,
} from './types/oscilloscope.types';

// Constants
export {
  DEFAULT_OSCILLOSCOPE_STATE,
  WEBSOCKET_CONFIG,
  CANVAS_CONFIG,
  DATA_CONFIG,
  PARAMETER_LIMITS,
  UI_CONFIG,
} from './constants/oscilloscope.constants';
