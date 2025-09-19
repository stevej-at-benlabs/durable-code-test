/**
 * Purpose: Custom React hook for oscilloscope state and control management
 * Scope: Hook for managing oscilloscope state, controls, and WebSocket communication
 * Overview: Provides centralized state management for oscilloscope functionality including
 *     waveform parameters, streaming controls, and WebSocket command dispatch. Integrates
 *     with useWebSocket and provides a complete oscilloscope control interface.
 * Dependencies: React hooks, WebSocket hook, oscilloscope types and constants
 * Exports: useOscilloscope hook
 * Interfaces: Hook return type with state, stats, and control methods
 * Implementation: Stateful hook managing oscilloscope configuration and WebSocket commands
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type {
  OscilloscopeState,
  OscilloscopeStats,
  WaveType,
} from '../types/oscilloscope.types';
import {
  DATA_CONFIG,
  DEFAULT_OSCILLOSCOPE_STATE,
} from '../constants/oscilloscope.constants';
import { useWebSocket } from './useWebSocket';

interface UseOscilloscopeReturn {
  state: OscilloscopeState;
  stats: OscilloscopeStats;
  dataBuffer: number[];
  startStreaming: () => void;
  stopStreaming: () => void;
  updateWaveform: (waveType: WaveType) => void;
  updateFrequency: (frequency: number) => void;
  updateAmplitude: (amplitude: number) => void;
  updateOffset: (offset: number) => void;
  updateTimeScale: (timeScale: number) => void;
  updateVoltScale: (voltScale: number) => void;
  updateTriggerLevel: (triggerLevel: number) => void;
  togglePause: () => void;
  clearBuffer: () => void;
  resetToDefaults: () => void;
  error: Error | null;
}

export function useOscilloscope(): UseOscilloscopeReturn {
  const [state, setState] = useState<OscilloscopeState>(DEFAULT_OSCILLOSCOPE_STATE);
  const [stats, setStats] = useState<OscilloscopeStats>({
    fps: 0,
    dataRate: 0,
    bufferSize: 0,
  });

  const dataBufferRef = useRef<number[]>([]);
  const frameCountRef = useRef<number>(0);
  const lastStatsUpdateRef = useRef<number>(performance.now());

  const { isConnected, lastData, send, error } = useWebSocket();

  // Update connection state
  useEffect(() => {
    setState((_prev) => ({
      ..._prev,
      isConnected,
      isStreaming: isConnected && _prev.isStreaming,
    }));
  }, [isConnected]);

  // Process incoming data
  useEffect(() => {
    if (!lastData || state.isPaused) return;

    // Update buffer with new samples
    const newBuffer = [...dataBufferRef.current, ...lastData.samples];
    dataBufferRef.current = newBuffer.slice(-DATA_CONFIG.MAX_BUFFER_SIZE);

    // Update stats
    const now = performance.now();
    const timeSinceLastUpdate = now - lastStatsUpdateRef.current;

    if (timeSinceLastUpdate >= DATA_CONFIG.FPS_CALCULATION_INTERVAL) {
      const fps = Math.round((frameCountRef.current * 1000) / timeSinceLastUpdate);

      setStats((_prev) => ({
        fps,
        dataRate: lastData.sample_rate,
        bufferSize: dataBufferRef.current.length,
      }));

      frameCountRef.current = 0;
      lastStatsUpdateRef.current = now;
    } else {
      setStats((prev) => ({
        ...prev,
        dataRate: lastData.sample_rate,
        bufferSize: dataBufferRef.current.length,
      }));
    }

    frameCountRef.current++;
  }, [lastData, state.isPaused]);

  // Start streaming
  const startStreaming = useCallback(() => {
    if (!isConnected) return;

    const success = send({
      command: 'start',
      wave_type: state.waveType,
      frequency: state.frequency,
      amplitude: state.amplitude,
      offset: state.offset,
    });

    if (success) {
      setState((prev) => ({ ...prev, isStreaming: true }));
    }
  }, [
    isConnected,
    send,
    state.waveType,
    state.frequency,
    state.amplitude,
    state.offset,
  ]);

  // Stop streaming
  const stopStreaming = useCallback(() => {
    if (!isConnected) return;

    const success = send({ command: 'stop' });

    if (success) {
      setState((prev) => ({ ...prev, isStreaming: false }));
    }
  }, [isConnected, send]);

  // Send configuration update
  const sendConfiguration = useCallback(
    (
      updates: Partial<
        Pick<OscilloscopeState, 'waveType' | 'frequency' | 'amplitude' | 'offset'>
      >,
    ) => {
      if (!isConnected || !state.isStreaming) return;

      send({
        command: 'configure',
        wave_type: updates.waveType ?? state.waveType,
        frequency: updates.frequency ?? state.frequency,
        amplitude: updates.amplitude ?? state.amplitude,
        offset: updates.offset ?? state.offset,
      });
    },
    [
      isConnected,
      state.isStreaming,
      state.waveType,
      state.frequency,
      state.amplitude,
      state.offset,
      send,
    ],
  );

  // Update waveform type
  const updateWaveform = useCallback(
    (waveType: WaveType) => {
      setState((prev) => ({ ...prev, waveType }));
      sendConfiguration({ waveType });
    },
    [sendConfiguration],
  );

  // Update frequency
  const updateFrequency = useCallback(
    (frequency: number) => {
      setState((prev) => ({ ...prev, frequency }));
      sendConfiguration({ frequency });
    },
    [sendConfiguration],
  );

  // Update amplitude
  const updateAmplitude = useCallback(
    (amplitude: number) => {
      setState((prev) => ({ ...prev, amplitude }));
      sendConfiguration({ amplitude });
    },
    [sendConfiguration],
  );

  // Update offset
  const updateOffset = useCallback(
    (offset: number) => {
      setState((prev) => ({ ...prev, offset }));
      sendConfiguration({ offset });
    },
    [sendConfiguration],
  );

  // Update time scale (UI only)
  const updateTimeScale = useCallback((timeScale: number) => {
    setState((prev) => ({ ...prev, timeScale }));
  }, []);

  // Update voltage scale (UI only)
  const updateVoltScale = useCallback((voltScale: number) => {
    setState((prev) => ({ ...prev, voltScale }));
  }, []);

  // Update trigger level (UI only)
  const updateTriggerLevel = useCallback((triggerLevel: number) => {
    setState((prev) => ({ ...prev, triggerLevel }));
  }, []);

  // Toggle pause
  const togglePause = useCallback(() => {
    setState((prev) => ({ ...prev, isPaused: !prev.isPaused }));
  }, []);

  // Clear buffer
  const clearBuffer = useCallback(() => {
    dataBufferRef.current = [];
    setStats((prev) => ({ ...prev, bufferSize: 0 }));
  }, []);

  // Reset only UI parameters to default values (like adjusting dials by hand)
  const resetToDefaults = useCallback(() => {
    setState((prev) => ({
      ...prev,
      waveType: DEFAULT_OSCILLOSCOPE_STATE.waveType,
      frequency: DEFAULT_OSCILLOSCOPE_STATE.frequency,
      amplitude: DEFAULT_OSCILLOSCOPE_STATE.amplitude,
      offset: DEFAULT_OSCILLOSCOPE_STATE.offset,
      timeScale: DEFAULT_OSCILLOSCOPE_STATE.timeScale,
      voltScale: DEFAULT_OSCILLOSCOPE_STATE.voltScale,
      triggerLevel: DEFAULT_OSCILLOSCOPE_STATE.triggerLevel,
    }));

    // If streaming, send the configuration update to backend
    if (isConnected && state.isStreaming) {
      sendConfiguration({
        waveType: DEFAULT_OSCILLOSCOPE_STATE.waveType,
        frequency: DEFAULT_OSCILLOSCOPE_STATE.frequency,
        amplitude: DEFAULT_OSCILLOSCOPE_STATE.amplitude,
        offset: DEFAULT_OSCILLOSCOPE_STATE.offset,
      });
    }
  }, [isConnected, state.isStreaming, sendConfiguration]);

  return {
    state,
    stats,
    dataBuffer: dataBufferRef.current,
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
  };
}
