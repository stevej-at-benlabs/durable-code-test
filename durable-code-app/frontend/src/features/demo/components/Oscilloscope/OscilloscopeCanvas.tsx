/**
 * Purpose: Oscilloscope canvas component for real-time waveform visualization
 * Scope: Canvas-based visualization component for oscilloscope data rendering
 * Overview: Provides a high-performance canvas component for rendering oscilloscope
 *     waveforms with grid, trigger lines, and real-time data visualization. Handles
 *     scaling, grid drawing, and waveform rendering optimizations.
 * Dependencies: React, canvas hook, oscilloscope types and constants
 * Exports: OscilloscopeCanvas component
 * Interfaces: Props interface for canvas configuration and data
 * Implementation: Canvas-based rendering with grid, waveform, and measurement overlays
 */

import React, { useCallback } from 'react';
import type { OscilloscopeCanvasProps } from '../../types/oscilloscope.types';
import { CANVAS_CONFIG } from '../../constants/oscilloscope.constants';
import { useCanvas } from '../../hooks/useCanvas';
import styles from './OscilloscopeCanvas.module.css';

export const OscilloscopeCanvas: React.FC<OscilloscopeCanvasProps> = ({
  data,
  state,
  stats,
}) => {
  // Draw grid on canvas
  const drawGrid = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      ctx.strokeStyle = CANVAS_CONFIG.GRID_COLOR;
      ctx.lineWidth = 1;

      // Draw vertical grid lines
      for (let i = 0; i <= CANVAS_CONFIG.GRID_DIVISIONS_HORIZONTAL; i++) {
        const x = (i * width) / CANVAS_CONFIG.GRID_DIVISIONS_HORIZONTAL;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      // Draw horizontal grid lines
      for (let i = 0; i <= CANVAS_CONFIG.GRID_DIVISIONS_VERTICAL; i++) {
        const y = (i * height) / CANVAS_CONFIG.GRID_DIVISIONS_VERTICAL;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw center lines
      ctx.strokeStyle = CANVAS_CONFIG.CENTER_LINE_COLOR;
      ctx.lineWidth = 2;

      // Center horizontal
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.lineTo(width, height / 2);
      ctx.stroke();

      // Center vertical
      ctx.beginPath();
      ctx.moveTo(width / 2, 0);
      ctx.lineTo(width / 2, height);
      ctx.stroke();
    },
    [],
  );

  // Draw waveform data
  const drawWaveform = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      if (data.length === 0) return;

      ctx.strokeStyle = CANVAS_CONFIG.WAVEFORM_COLOR;
      ctx.lineWidth = 2;
      ctx.beginPath();

      // Calculate samples to display based on time scale
      // Each division represents timeScale milliseconds, and we have 10 divisions
      const timeWindow =
        (state.timeScale * CANVAS_CONFIG.GRID_DIVISIONS_HORIZONTAL) / 1000; // Convert to seconds
      const samplesToShow = Math.min(data.length, Math.floor(timeWindow * 1000)); // Assuming 1000 samples/sec
      const startIndex = Math.max(0, data.length - samplesToShow);
      const displayData = data.slice(startIndex);

      const samplesPerPixel = Math.max(1, Math.floor(displayData.length / width));
      const pixelStep = width / Math.min(width, displayData.length);

      for (let i = 0; i < Math.min(width, displayData.length); i++) {
        const sampleIndex = Math.floor(i * samplesPerPixel);
        const value = displayData[sampleIndex];

        // Map value to canvas coordinates
        const x = i * pixelStep;
        const y = height / 2 - (value * height) / (4 * state.voltScale);

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    },
    [data, state.timeScale, state.voltScale],
  );

  // Draw trigger level
  const drawTrigger = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      if (state.isPaused) return;

      ctx.strokeStyle = CANVAS_CONFIG.TRIGGER_COLOR;
      ctx.lineWidth = 1;
      ctx.setLineDash([5, 5]);
      ctx.beginPath();

      const triggerY =
        height / 2 - (state.triggerLevel * height) / (4 * state.voltScale);
      ctx.moveTo(0, triggerY);
      ctx.lineTo(width, triggerY);
      ctx.stroke();
      ctx.setLineDash([]);
    },
    [state.isPaused, state.triggerLevel, state.voltScale],
  );

  // Draw measurements and labels
  const drawMeasurements = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      ctx.fillStyle = CANVAS_CONFIG.TEXT_COLOR;
      ctx.font = '12px monospace';

      // Draw scale information at bottom with proper margin
      const bottomMargin = 25;
      const lineSpacing = 18;
      ctx.fillText(
        `${state.timeScale} ms/div`,
        10,
        height - bottomMargin - lineSpacing * 2,
      );
      ctx.fillText(`${state.voltScale} V/div`, 10, height - bottomMargin - lineSpacing);
      ctx.fillText(`Freq: ${state.frequency.toFixed(1)} Hz`, 10, height - bottomMargin);

      // Draw performance metrics at top
      ctx.fillText(`FPS: ${stats.fps}`, width - 80, 20);
    },
    [state.timeScale, state.voltScale, state.frequency, stats.fps],
  );

  // Main drawing function
  const draw = useCallback(
    (ctx: CanvasRenderingContext2D, canvas: HTMLCanvasElement) => {
      const { width, height } = canvas;

      // Clear canvas
      ctx.fillStyle = CANVAS_CONFIG.BACKGROUND_COLOR;
      ctx.fillRect(0, 0, width, height);

      // Draw components
      drawGrid(ctx, width, height);
      drawWaveform(ctx, width, height);
      drawTrigger(ctx, width, height);
      drawMeasurements(ctx, width, height);
    },
    [drawGrid, drawWaveform, drawTrigger, drawMeasurements],
  );

  const { canvasRef } = useCanvas(draw, {
    autoResize: true,
  });

  return (
    <div className={styles.container}>
      <canvas
        ref={canvasRef}
        className={styles.canvas}
        style={{
          width: '100%',
          height: '400px',
          background: CANVAS_CONFIG.BACKGROUND_COLOR,
          border: `2px solid ${CANVAS_CONFIG.BORDER_COLOR}`,
          borderRadius: CANVAS_CONFIG.BORDER_RADIUS,
        }}
      />
    </div>
  );
};
