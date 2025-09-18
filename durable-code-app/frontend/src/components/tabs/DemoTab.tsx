/**
 * Purpose: Interactive oscilloscope demonstration tab component for the durable code framework
 * Scope: Tab component displaying real-time oscilloscope with configurable waveforms
 * Overview: Provides an interactive oscilloscope demonstration with real-time waveform streaming.
 *     Supports sine waves, square waves, and white noise generation with adjustable parameters.
 *     Features include zoom, pan, scale adjustment, and real-time WebSocket data streaming.
 * Dependencies: React, TypeScript, WebSocket API, Canvas API
 * Exports: DemoTab component (named export)
 * Props/Interfaces: No external props - self-contained tab component
 * State/Behavior: Manages WebSocket connection, waveform parameters, and visualization settings
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import type { ReactElement } from 'react';

interface OscilloscopeState {
  isConnected: boolean;
  isStreaming: boolean;
  waveType: 'sine' | 'square' | 'noise';
  frequency: number;
  amplitude: number;
  offset: number;
  zoom: number;
  timeScale: number;
  voltScale: number;
  triggerLevel: number;
  isPaused: boolean;
}

interface OscilloscopeData {
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

export function DemoTab(): ReactElement {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const dataBufferRef = useRef<number[]>([]);
  const animationFrameRef = useRef<number>();
  const frameCountRef = useRef<number>(0);

  const [state, setState] = useState<OscilloscopeState>({
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
  });

  const [stats, setStats] = useState({
    fps: 0,
    dataRate: 0,
    bufferSize: 0,
  });

  // Draw grid on canvas
  const drawGrid = useCallback(
    (ctx: CanvasRenderingContext2D, width: number, height: number) => {
      ctx.strokeStyle = '#2a2a2a';
      ctx.lineWidth = 1;

      // Draw vertical grid lines (10 divisions)
      for (let i = 0; i <= 10; i++) {
        const x = (i * width) / 10;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      // Draw horizontal grid lines (8 divisions)
      for (let i = 0; i <= 8; i++) {
        const y = (i * height) / 8;
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw center lines
      ctx.strokeStyle = '#3a3a3a';
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

  // Draw waveform on canvas
  const drawWaveform = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;

    // Clear canvas
    ctx.fillStyle = '#1a1a1a';
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    drawGrid(ctx, width, height);

    // Draw waveform
    const data = dataBufferRef.current;
    if (data.length > 0) {
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.beginPath();

      const samplesPerPixel = Math.max(1, Math.floor(data.length / width));
      const pixelStep = width / Math.min(width, data.length);

      for (let i = 0; i < Math.min(width, data.length); i++) {
        const sampleIndex = Math.floor(i * samplesPerPixel);
        const value = data[sampleIndex];

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

      // Draw trigger level
      if (!state.isPaused) {
        ctx.strokeStyle = '#ff9900';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        const triggerY =
          height / 2 - (state.triggerLevel * height) / (4 * state.voltScale);
        ctx.moveTo(0, triggerY);
        ctx.lineTo(width, triggerY);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Draw measurements
    ctx.fillStyle = '#00ff00';
    ctx.font = '12px monospace';
    ctx.fillText(`${state.timeScale} ms/div`, 10, 20);
    ctx.fillText(`${state.voltScale} V/div`, 10, 35);
    ctx.fillText(`Freq: ${state.frequency.toFixed(1)} Hz`, 10, 50);
    ctx.fillText(`FPS: ${stats.fps}`, width - 80, 20);

    // Increment frame counter
    frameCountRef.current++;

    animationFrameRef.current = requestAnimationFrame(drawWaveform);
  }, [state, stats, drawGrid, frameCountRef]);

  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    // Connect directly to backend port
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname;
    const port = 8000; // Backend port
    const ws = new WebSocket(`${protocol}//${host}:${port}/api/oscilloscope/stream`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setState((prev) => ({ ...prev, isConnected: true }));
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setState((prev) => ({ ...prev, isConnected: false, isStreaming: false }));
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const data: OscilloscopeData = JSON.parse(event.data);

        // Update buffer with new samples
        if (!state.isPaused) {
          const maxBufferSize = 2000;
          dataBufferRef.current = [...dataBufferRef.current, ...data.samples].slice(
            -maxBufferSize,
          );

          // Update stats
          setStats((prev) => ({
            ...prev,
            dataRate: data.sample_rate,
            bufferSize: dataBufferRef.current.length,
          }));
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    wsRef.current = ws;
  }, [state.isPaused]);

  // Send command to WebSocket
  const sendCommand = useCallback((command: Record<string, unknown>) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(command));
    }
  }, []);

  // Start streaming
  const startStreaming = useCallback(() => {
    sendCommand({
      command: 'start',
      wave_type: state.waveType,
      frequency: state.frequency,
      amplitude: state.amplitude,
      offset: state.offset,
    });
    setState((prev) => ({ ...prev, isStreaming: true }));
  }, [state, sendCommand]);

  // Stop streaming
  const stopStreaming = useCallback(() => {
    sendCommand({ command: 'stop' });
    setState((prev) => ({ ...prev, isStreaming: false }));
  }, [sendCommand]);

  // Update wave parameters
  const updateWaveform = useCallback(
    (waveType: 'sine' | 'square' | 'noise') => {
      setState((prev) => ({ ...prev, waveType }));
      if (state.isStreaming) {
        sendCommand({
          command: 'configure',
          wave_type: waveType,
          frequency: state.frequency,
          amplitude: state.amplitude,
          offset: state.offset,
        });
      }
    },
    [state, sendCommand],
  );

  // Handle parameter changes
  const handleFrequencyChange = useCallback(
    (value: number) => {
      setState((prev) => ({ ...prev, frequency: value }));
      if (state.isStreaming) {
        sendCommand({
          command: 'configure',
          wave_type: state.waveType,
          frequency: value,
          amplitude: state.amplitude,
          offset: state.offset,
        });
      }
    },
    [state, sendCommand],
  );

  const handleAmplitudeChange = useCallback(
    (value: number) => {
      setState((prev) => ({ ...prev, amplitude: value }));
      if (state.isStreaming) {
        sendCommand({
          command: 'configure',
          wave_type: state.waveType,
          frequency: state.frequency,
          amplitude: value,
          offset: state.offset,
        });
      }
    },
    [state, sendCommand],
  );

  const handleOffsetChange = useCallback(
    (value: number) => {
      setState((prev) => ({ ...prev, offset: value }));
      if (state.isStreaming) {
        sendCommand({
          command: 'configure',
          wave_type: state.waveType,
          frequency: state.frequency,
          amplitude: state.amplitude,
          offset: value,
        });
      }
    },
    [state, sendCommand],
  );

  // Initialize canvas and WebSocket
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    connectWebSocket();

    // Start drawing
    drawWaveform();

    // Calculate FPS
    let lastTime = performance.now();

    const fpsInterval = setInterval(() => {
      const currentTime = performance.now();
      const deltaTime = currentTime - lastTime;
      const fps = Math.round((frameCountRef.current * 1000) / deltaTime);
      setStats((prev) => ({ ...prev, fps }));
      frameCountRef.current = 0;
      lastTime = currentTime;
    }, 1000);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
      clearInterval(fpsInterval);
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle canvas resize
  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="tab-content demo-tab">
      <div className="tab-header">
        <div className="tab-title-section">
          <h1 className="tab-title">
            <span className="tab-icon">📡</span>
            Oscilloscope Demo
          </h1>
          <p className="tab-subtitle">
            Real-time waveform visualization with WebSocket streaming
          </p>
        </div>
      </div>

      <div className="tab-body">
        <div className="content-grid">
          {/* Oscilloscope Display */}
          <section className="oscilloscope-section">
            <div className="content-card">
              <div className="oscilloscope-container">
                <canvas
                  ref={canvasRef}
                  className="oscilloscope-canvas"
                  style={{
                    width: '100%',
                    height: '400px',
                    background: '#1a1a1a',
                    border: '2px solid #333',
                    borderRadius: '8px',
                  }}
                />
              </div>

              {/* Control Panel */}
              <div className="control-panel" style={{ marginTop: '20px' }}>
                <div
                  className="control-row"
                  style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}
                >
                  <button
                    onClick={startStreaming}
                    disabled={!state.isConnected || state.isStreaming}
                    className="control-button"
                    style={{
                      padding: '10px 20px',
                      background: state.isStreaming ? '#555' : '#00a86b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: state.isStreaming ? 'not-allowed' : 'pointer',
                    }}
                  >
                    ▶ Start
                  </button>
                  <button
                    onClick={stopStreaming}
                    disabled={!state.isConnected || !state.isStreaming}
                    className="control-button"
                    style={{
                      padding: '10px 20px',
                      background: !state.isStreaming ? '#555' : '#ff4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: !state.isStreaming ? 'not-allowed' : 'pointer',
                    }}
                  >
                    ⏹ Stop
                  </button>
                  <button
                    onClick={() =>
                      setState((prev) => ({ ...prev, isPaused: !prev.isPaused }))
                    }
                    className="control-button"
                    style={{
                      padding: '10px 20px',
                      background: state.isPaused ? '#ffa500' : '#555',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                    }}
                  >
                    {state.isPaused ? '⏸ Paused' : '⏸ Pause'}
                  </button>
                  <button
                    onClick={() => (dataBufferRef.current = [])}
                    className="control-button"
                    style={{
                      padding: '10px 20px',
                      background: '#555',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                    }}
                  >
                    🗑️ Clear
                  </button>
                </div>

                {/* Waveform Selection */}
                <div className="waveform-selection" style={{ marginBottom: '15px' }}>
                  <h3>Waveform Type</h3>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => updateWaveform('sine')}
                      className={state.waveType === 'sine' ? 'active' : ''}
                      style={{
                        padding: '10px 20px',
                        background: state.waveType === 'sine' ? '#00a86b' : '#555',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                      }}
                    >
                      ∿ Sine Wave
                    </button>
                    <button
                      onClick={() => updateWaveform('square')}
                      className={state.waveType === 'square' ? 'active' : ''}
                      style={{
                        padding: '10px 20px',
                        background: state.waveType === 'square' ? '#00a86b' : '#555',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                      }}
                    >
                      ⊓ Square Wave
                    </button>
                    <button
                      onClick={() => updateWaveform('noise')}
                      className={state.waveType === 'noise' ? 'active' : ''}
                      style={{
                        padding: '10px 20px',
                        background: state.waveType === 'noise' ? '#00a86b' : '#555',
                        color: 'white',
                        border: 'none',
                        borderRadius: '5px',
                        cursor: 'pointer',
                      }}
                    >
                      ≋ White Noise
                    </button>
                  </div>
                </div>

                {/* Parameter Controls */}
                <div
                  className="parameter-controls"
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '15px',
                  }}
                >
                  <div className="control-group">
                    <label>Frequency (Hz): {state.frequency}</label>
                    <input
                      type="range"
                      min="0.1"
                      max="100"
                      step="0.1"
                      value={state.frequency}
                      onChange={(e) =>
                        handleFrequencyChange(parseFloat(e.target.value))
                      }
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div className="control-group">
                    <label>Amplitude: {state.amplitude.toFixed(1)}</label>
                    <input
                      type="range"
                      min="0.1"
                      max="10"
                      step="0.1"
                      value={state.amplitude}
                      onChange={(e) =>
                        handleAmplitudeChange(parseFloat(e.target.value))
                      }
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div className="control-group">
                    <label>Time Scale (ms/div): {state.timeScale}</label>
                    <input
                      type="range"
                      min="1"
                      max="100"
                      step="1"
                      value={state.timeScale}
                      onChange={(e) =>
                        setState((prev) => ({
                          ...prev,
                          timeScale: parseInt(e.target.value),
                        }))
                      }
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div className="control-group">
                    <label>Voltage Scale (V/div): {state.voltScale.toFixed(1)}</label>
                    <input
                      type="range"
                      min="0.1"
                      max="10"
                      step="0.1"
                      value={state.voltScale}
                      onChange={(e) =>
                        setState((prev) => ({
                          ...prev,
                          voltScale: parseFloat(e.target.value),
                        }))
                      }
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div className="control-group">
                    <label>Trigger Level: {state.triggerLevel.toFixed(1)}</label>
                    <input
                      type="range"
                      min="-5"
                      max="5"
                      step="0.1"
                      value={state.triggerLevel}
                      onChange={(e) =>
                        setState((prev) => ({
                          ...prev,
                          triggerLevel: parseFloat(e.target.value),
                        }))
                      }
                      style={{ width: '100%' }}
                    />
                  </div>
                  <div className="control-group">
                    <label>DC Offset: {state.offset.toFixed(1)}</label>
                    <input
                      type="range"
                      min="-10"
                      max="10"
                      step="0.1"
                      value={state.offset}
                      onChange={(e) => handleOffsetChange(parseFloat(e.target.value))}
                      style={{ width: '100%' }}
                    />
                  </div>
                </div>
              </div>

              {/* Status Information */}
              <div
                className="status-panel"
                style={{
                  marginTop: '20px',
                  padding: '10px',
                  background: '#2a2a2a',
                  borderRadius: '5px',
                }}
              >
                <h3>Connection Status</h3>
                <div style={{ display: 'flex', gap: '20px' }}>
                  <span>
                    Connection:{' '}
                    <span style={{ color: state.isConnected ? '#00ff00' : '#ff4444' }}>
                      {state.isConnected ? '● Connected' : '○ Disconnected'}
                    </span>
                  </span>
                  <span>
                    Streaming:{' '}
                    <span style={{ color: state.isStreaming ? '#00ff00' : '#666' }}>
                      {state.isStreaming ? '● Active' : '○ Inactive'}
                    </span>
                  </span>
                  <span>Data Rate: {stats.dataRate} S/s</span>
                  <span>Buffer: {stats.bufferSize} samples</span>
                </div>
              </div>
            </div>
          </section>

          {/* Documentation section */}
          <section className="documentation-section">
            <div className="content-card">
              <h2>About This Demo</h2>
              <p>
                This interactive oscilloscope demonstrates real-time data streaming
                using WebSockets and canvas-based visualization. The backend generates
                waveforms in real-time and streams them to the frontend for display.
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
            </div>
          </section>
        </div>
      </div>

      <div className="tab-footer">
        <div className="footer-content">
          <p className="footer-note">
            This oscilloscope demo showcases real-time data streaming and visualization
            capabilities of the durable code framework.
          </p>
        </div>
      </div>
    </div>
  );
}
