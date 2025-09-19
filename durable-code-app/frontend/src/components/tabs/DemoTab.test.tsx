/**
 * Purpose: Unit tests for DemoTab oscilloscope component
 * Scope: Test rendering, WebSocket connection, user interactions, and waveform controls
 * Overview: Comprehensive test suite for the DemoTab component including rendering tests,
 *     WebSocket mock testing, control interaction verification, and canvas rendering checks.
 * Dependencies: React Testing Library, vitest, WebSocket mock
 * Exports: Test suite for DemoTab component
 * Interfaces: vitest test functions
 * Implementation: Component testing with mocked WebSocket and canvas
 */

import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { DemoTab } from '../../features/demo';

// Mock WebSocket
class MockWebSocket {
  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  sentMessages: Record<string, unknown>[] = [];

  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSING = 2;
  static CLOSED = 3;

  constructor(url: string) {
    this.url = url;
    this.readyState = MockWebSocket.CONNECTING;

    // Simulate connection opening
    setTimeout(() => {
      act(() => {
        this.readyState = MockWebSocket.OPEN;
        if (this.onopen) {
          this.onopen(new Event('open'));
        }
      });
    }, 0);
  }

  send(data: string) {
    if (this.readyState === MockWebSocket.OPEN) {
      this.sentMessages.push(JSON.parse(data));
    }
  }

  close() {
    act(() => {
      this.readyState = MockWebSocket.CLOSED;
      if (this.onclose) {
        this.onclose(new CloseEvent('close'));
      }
    });
  }

  simulateMessage(data: Record<string, unknown>) {
    act(() => {
      if (this.onmessage) {
        this.onmessage(
          new MessageEvent('message', {
            data: JSON.stringify(data),
          }),
        );
      }
    });
  }
}

// Mock canvas context
const mockCanvasContext = {
  fillStyle: '',
  strokeStyle: '',
  lineWidth: 1,
  font: '',
  fillRect: vi.fn(),
  strokeRect: vi.fn(),
  fillText: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  stroke: vi.fn(),
  setLineDash: vi.fn(),
  getContext: vi.fn(() => mockCanvasContext),
};

describe('DemoTab Component', () => {
  let mockWebSocket: MockWebSocket;
  let originalWebSocket: typeof WebSocket;

  beforeEach(() => {
    // Save original WebSocket
    originalWebSocket = global.WebSocket as typeof WebSocket;

    // Replace with mock
    // @ts-expect-error - mocking WebSocket for testing
    global.WebSocket = vi.fn((url: string) => {
      mockWebSocket = new MockWebSocket(url);
      return mockWebSocket;
    }) as typeof WebSocket;
    // Add static properties to the mock WebSocket
    Object.assign(global.WebSocket, {
      CONNECTING: MockWebSocket.CONNECTING,
      OPEN: MockWebSocket.OPEN,
      CLOSING: MockWebSocket.CLOSING,
      CLOSED: MockWebSocket.CLOSED,
    });

    // Mock canvas
    // @ts-expect-error - mocking canvas for testing
    HTMLCanvasElement.prototype.getContext = vi.fn(() => mockCanvasContext);

    // Mock requestAnimationFrame
    global.requestAnimationFrame = vi.fn(
      (cb) => setTimeout(cb, 0) as unknown as number,
    ) as typeof requestAnimationFrame;
    global.cancelAnimationFrame = vi.fn();
  });

  afterEach(() => {
    // Restore original WebSocket
    global.WebSocket = originalWebSocket;
    vi.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render the component with title', () => {
      render(<DemoTab />);
      expect(screen.getByText('Oscilloscope Demo')).toBeInTheDocument();
      expect(
        screen.getByText(/Built entirely by AI while the human went to dinner/),
      ).toBeInTheDocument();
    });

    it('should render control buttons', () => {
      render(<DemoTab />);
      expect(screen.getByText('▶ Start')).toBeInTheDocument();
      expect(screen.getByText('⏹ Stop')).toBeInTheDocument();
      expect(screen.getByText('⏸ Pause')).toBeInTheDocument();
      expect(screen.getByText('🗑️ Clear')).toBeInTheDocument();
    });

    it('should render waveform selection buttons', () => {
      render(<DemoTab />);
      expect(screen.getByText('∿ Sine Wave')).toBeInTheDocument();
      expect(screen.getByText('⊓ Square Wave')).toBeInTheDocument();
      expect(screen.getByText('≋ White Noise')).toBeInTheDocument();
    });

    it('should render parameter controls', () => {
      render(<DemoTab />);
      expect(screen.getByText(/Frequency \(Hz\)/)).toBeInTheDocument();
      expect(screen.getByText(/Amplitude:/)).toBeInTheDocument();
      expect(screen.getByText(/Time Scale/)).toBeInTheDocument();
      expect(screen.getByText(/Voltage Scale/)).toBeInTheDocument();
      expect(screen.getByText(/Trigger Level/)).toBeInTheDocument();
      expect(screen.getByText(/DC Offset/)).toBeInTheDocument();
    });

    it('should render canvas element', () => {
      const { container } = render(<DemoTab />);
      const canvas = container.querySelector('canvas');
      expect(canvas).toBeInTheDocument();
      expect(canvas).toHaveClass('oscilloscope-canvas');
    });

    it('should render documentation section', () => {
      render(<DemoTab />);
      expect(screen.getByText('About This Demo')).toBeInTheDocument();
      expect(screen.getByText('Features')).toBeInTheDocument();
      expect(screen.getByText('Technical Implementation')).toBeInTheDocument();
    });
  });

  describe('WebSocket Connection', () => {
    it('should establish WebSocket connection on mount', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(global.WebSocket).toHaveBeenCalledWith(
          expect.stringContaining('/api/oscilloscope/stream'),
        );
      });
    });

    it('should show connected status when WebSocket opens', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        const statusText = screen.getByText(/Connection:/);
        expect(statusText.parentElement?.textContent).toContain('Connected');
      });
    });

    it('should show disconnected status when WebSocket closes', async () => {
      render(<DemoTab />);

      // Wait for connection
      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Close WebSocket
      mockWebSocket.close();

      await waitFor(() => {
        const statusText = screen.getByText(/Connection:/);
        expect(statusText.parentElement?.textContent).toContain('Disconnected');
      });
    });
  });

  describe('Control Interactions', () => {
    it('should send start command when Start button is clicked', async () => {
      render(<DemoTab />);

      // Wait for connection
      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      const startButton = screen.getByText('▶ Start');
      fireEvent.click(startButton);

      await waitFor(() => {
        const sentMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'start',
        );
        expect(sentMessage).toBeDefined();
        expect(sentMessage?.wave_type).toBe('sine');
      });
    });

    it('should send stop command when Stop button is clicked', async () => {
      render(<DemoTab />);

      // Wait for connection and start streaming
      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming first
      const startButton = screen.getByText('▶ Start');
      fireEvent.click(startButton);

      // Then stop
      const stopButton = screen.getByText('⏹ Stop');
      fireEvent.click(stopButton);

      await waitFor(() => {
        const sentMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'stop',
        );
        expect(sentMessage).toBeDefined();
      });
    });

    it('should toggle pause state when Pause button is clicked', () => {
      render(<DemoTab />);

      const pauseButton = screen.getByText('⏸ Pause');
      fireEvent.click(pauseButton);

      expect(screen.getByText('⏸ Paused')).toBeInTheDocument();
    });

    it('should clear buffer when Clear button is clicked', () => {
      render(<DemoTab />);

      const clearButton = screen.getByText('🗑️ Clear');
      fireEvent.click(clearButton);

      // Canvas should be redrawn (mocked function called)
      expect(mockCanvasContext.fillRect).toHaveBeenCalled();
    });
  });

  describe('Waveform Selection', () => {
    it('should send configure command when sine wave is selected', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming first
      fireEvent.click(screen.getByText('▶ Start'));

      const sineButton = screen.getByText('∿ Sine Wave');
      fireEvent.click(sineButton);

      await waitFor(() => {
        const configMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'configure' && msg.wave_type === 'sine',
        );
        expect(configMessage).toBeDefined();
      });
    });

    it('should send configure command when square wave is selected', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming first
      fireEvent.click(screen.getByText('▶ Start'));

      const squareButton = screen.getByText('⊓ Square Wave');
      fireEvent.click(squareButton);

      await waitFor(() => {
        const configMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'configure' && msg.wave_type === 'square',
        );
        expect(configMessage).toBeDefined();
      });
    });

    it('should send configure command when white noise is selected', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming first
      fireEvent.click(screen.getByText('▶ Start'));

      const noiseButton = screen.getByText('≋ White Noise');
      fireEvent.click(noiseButton);

      await waitFor(() => {
        const configMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'configure' && msg.wave_type === 'noise',
        );
        expect(configMessage).toBeDefined();
      });
    });
  });

  describe('Parameter Controls', () => {
    it('should update frequency when slider is changed', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming
      fireEvent.click(screen.getByText('▶ Start'));

      // Find all sliders and change the first one (frequency)
      const sliders = screen.getAllByRole('slider');
      expect(sliders.length).toBeGreaterThan(0);

      // Change the first slider which should be frequency
      fireEvent.change(sliders[0], { target: { value: '25' } });

      await waitFor(() => {
        const configMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'configure' && msg.frequency === 25,
        );
        expect(configMessage).toBeDefined();
      });
    });

    it('should update amplitude when slider is changed', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Start streaming
      fireEvent.click(screen.getByText('▶ Start'));

      // Find all sliders and change the second one (amplitude)
      const sliders = screen.getAllByRole('slider');
      expect(sliders.length).toBeGreaterThan(1);

      // Change the second slider which should be amplitude
      fireEvent.change(sliders[1], { target: { value: '2.5' } });

      await waitFor(() => {
        const configMessage = mockWebSocket.sentMessages.find(
          (msg) => msg.command === 'configure' && msg.amplitude === 2.5,
        );
        expect(configMessage).toBeDefined();
      });
    });
  });

  describe('Data Reception', () => {
    it('should process incoming oscilloscope data', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Simulate incoming data
      const testData = {
        timestamp: Date.now(),
        samples: [0, 0.5, 1, 0.5, 0, -0.5, -1, -0.5],
        sample_rate: 1000,
        wave_type: 'sine',
        parameters: {
          frequency: 10,
          amplitude: 1,
          offset: 0,
        },
      };

      mockWebSocket.simulateMessage(testData);

      // Canvas should be updated
      await waitFor(() => {
        expect(mockCanvasContext.stroke).toHaveBeenCalled();
      });
    });

    it('should update stats when data is received', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      // Simulate incoming data
      const testData = {
        timestamp: Date.now(),
        samples: Array(100).fill(0),
        sample_rate: 1000,
        wave_type: 'sine',
        parameters: {
          frequency: 10,
          amplitude: 1,
          offset: 0,
        },
      };

      mockWebSocket.simulateMessage(testData);

      await waitFor(() => {
        expect(screen.getByText(/Data Rate: 1000 S\/s/)).toBeInTheDocument();
      });
    });
  });

  describe('Canvas Rendering', () => {
    it('should draw grid on canvas', () => {
      render(<DemoTab />);

      // Grid drawing involves multiple stroke calls
      expect(mockCanvasContext.beginPath).toHaveBeenCalled();
      expect(mockCanvasContext.moveTo).toHaveBeenCalled();
      expect(mockCanvasContext.lineTo).toHaveBeenCalled();
      expect(mockCanvasContext.stroke).toHaveBeenCalled();
    });

    it('should display measurements on canvas', () => {
      render(<DemoTab />);

      // Should draw text for measurements
      expect(mockCanvasContext.fillText).toHaveBeenCalledWith(
        expect.stringContaining('ms/div'),
        expect.any(Number),
        expect.any(Number),
      );
    });
  });

  describe('Button States', () => {
    it('should disable Start button when streaming', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      const startButton = screen.getByText('▶ Start');
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(startButton).toBeDisabled();
      });
    });

    it('should disable Stop button when not streaming', () => {
      render(<DemoTab />);

      const stopButton = screen.getByText('⏹ Stop');
      expect(stopButton).toBeDisabled();
    });

    it('should enable Stop button when streaming', async () => {
      render(<DemoTab />);

      await waitFor(() => {
        expect(mockWebSocket).toBeDefined();
      });

      const startButton = screen.getByText('▶ Start');
      fireEvent.click(startButton);

      const stopButton = screen.getByText('⏹ Stop');
      await waitFor(() => {
        expect(stopButton).not.toBeDisabled();
      });
    });
  });
});
