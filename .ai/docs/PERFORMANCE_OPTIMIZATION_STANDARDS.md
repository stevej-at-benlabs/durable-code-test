# Performance Optimization Standards

## Overview
This document establishes standards and patterns for performance optimization in React applications, particularly for real-time data handling, WebSocket communication, and canvas rendering.

## Core Principles

### 1. Eliminate Polling Loops
**Rule**: Never use `setInterval` for state synchronization. Use event-driven patterns instead.

**Bad**:
```typescript
// DON'T: Polling-based state sync
useEffect(() => {
  const interval = setInterval(() => {
    if (service && service.isConnected !== isConnected) {
      setIsConnected(service.isConnected);
    }
  }, 500); // Creates unnecessary 500ms polling
  return () => clearInterval(interval);
}, [service, isConnected]);
```

**Good**:
```typescript
// DO: Event-driven state sync
useEffect(() => {
  if (service && service.isConnected !== isConnected) {
    setIsConnected(service.isConnected); // One-time sync
  }
}, [service?.isConnected]); // Dependency-driven updates
```

### 2. Use Efficient Data Structures
**Rule**: Use `Float32Array` and circular buffers for high-frequency data updates.

**Implementation Pattern**:
```typescript
// Use CircularBuffer for real-time data
class CircularBuffer {
  private buffer: Float32Array;
  private head: number = 0;
  private size: number = 0;

  constructor(private capacity: number) {
    this.buffer = new Float32Array(capacity);
  }

  push(items: number[]): void {
    // Efficient batch insertion without array spreading
  }

  getView(): Float32Array {
    // Return view without copying data
  }
}
```

### 3. Data-Driven Rendering
**Rule**: Replace continuous animation loops with data-driven rendering.

**Bad**:
```typescript
// DON'T: Continuous animation loop
useEffect(() => {
  startAnimation(); // Runs continuously regardless of data changes
}, []);
```

**Good**:
```typescript
// DO: Data-driven rendering
useEffect(() => {
  if (drawFunction) {
    drawFunction(); // Only renders when data changes
  }
}, [drawFunction]); // Triggered by actual data updates
```

## Performance Monitoring Repository

### PerformanceMonitor Pattern
Use singleton pattern for application-wide performance tracking:

```typescript
// Singleton performance monitor
class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetrics = { fps: 0, renderTime: 0, memoryUsage: 0 };

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  updateMetrics(newMetrics: Partial<PerformanceMetrics>): void {
    // Update metrics with thresholds and alerts
  }
}
```

### React Hook Integration
```typescript
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>();
  const monitor = PerformanceMonitor.getInstance();

  useEffect(() => {
    return monitor.subscribe(setMetrics);
  }, [monitor]);

  return metrics;
}
```

## WebSocket Optimization Patterns

### Event-Driven Updates
```typescript
export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastData, setLastData] = useState<WebSocketData | null>(null);

  // Event-driven connection state sync
  useEffect(() => {
    if (serviceRef.current && serviceRef.current.isConnected !== isConnected) {
      setIsConnected(serviceRef.current.isConnected);
    }
  }, [serviceRef.current?.isConnected]); // No polling!

  // Data updates triggered by actual messages
  useEffect(() => {
    const service = serviceRef.current;
    if (!service) return;

    const handleData = (data: WebSocketData) => setLastData(data);
    service.subscribe(handleData);
    return () => service.unsubscribe(handleData);
  }, []);
}
```

## Canvas Rendering Optimization

### Efficient Drawing Patterns
```typescript
export function useCanvas(canvasRef: RefObject<HTMLCanvasElement>) {
  const [drawFunction, setDrawFunction] = useState<(() => void) | null>(null);

  // Only redraw when draw function changes (data-driven)
  useEffect(() => {
    if (drawFunction) {
      drawFunction();
    }
  }, [drawFunction]);

  const updateDrawFunction = useCallback((newDrawFn: () => void) => {
    setDrawFunction(() => newDrawFn);
  }, []);

  return { updateDrawFunction };
}
```

## Type Safety for Performance

### Use Typed Arrays
```typescript
// Use Float32Array for numerical data
interface OscilloscopeData {
  samples: Float32Array; // Not number[]
  sampleRate: number;
  timestamp: number;
}

// Return typed arrays from hooks
export function useOscilloscope(): {
  dataBuffer: Float32Array; // Not number[]
  // ... other properties
} {
  const dataBufferRef = useRef<CircularBuffer>(new CircularBuffer(MAX_SIZE));

  return {
    dataBuffer: dataBufferRef.current.getView(), // Returns Float32Array
  };
}
```

## Memory Management

### Cleanup Patterns
```typescript
useEffect(() => {
  const buffer = new CircularBuffer(MAX_SIZE);
  const monitor = PerformanceMonitor.getInstance();

  // Setup subscriptions
  const unsubscribe = monitor.subscribe(handleMetrics);

  return () => {
    // Always cleanup
    unsubscribe();
    buffer.clear();
  };
}, []);
```

### Prevent Memory Leaks
```typescript
// Use refs for persistent objects
const dataBufferRef = useRef<CircularBuffer>(new CircularBuffer(MAX_SIZE));
const frameCountRef = useRef<number>(0);

// Avoid creating objects in render
const memoizedValue = useMemo(() => {
  return expensiveCalculation();
}, [dependencies]);
```

## Performance Thresholds

### Monitoring Thresholds
```typescript
const PERFORMANCE_THRESHOLDS = {
  MIN_FPS: 30,
  MAX_RENDER_TIME: 16, // 16ms for 60fps
  MAX_MEMORY_USAGE: 100 * 1024 * 1024, // 100MB
  MAX_BUFFER_SIZE: 10000,
} as const;
```

### Alert System
```typescript
class PerformanceMonitor {
  private checkThresholds(metrics: PerformanceMetrics): void {
    if (metrics.fps < PERFORMANCE_THRESHOLDS.MIN_FPS) {
      this.emit('performance-warning', { type: 'low-fps', value: metrics.fps });
    }
    // ... other threshold checks
  }
}
```

## Integration Standards

### Component Integration
```typescript
function PerformantComponent() {
  const performanceMetrics = usePerformanceMetrics();
  const { dataBuffer, updateFrequency } = useOscilloscope();
  const { updateDrawFunction } = useCanvas(canvasRef);

  // Data-driven updates
  useEffect(() => {
    const drawFn = () => drawWaveform(dataBuffer, canvasRef.current);
    updateDrawFunction(drawFn);
  }, [dataBuffer, updateDrawFunction]);

  return <canvas ref={canvasRef} />;
}
```

### Testing Performance Optimizations
```typescript
// Test that polling is eliminated
test('should not use polling for state sync', () => {
  jest.spyOn(global, 'setInterval');
  render(<WebSocketComponent />);
  expect(setInterval).not.toHaveBeenCalled();
});

// Test efficient data structures
test('should use Float32Array for data buffer', () => {
  const { result } = renderHook(() => useOscilloscope());
  expect(result.current.dataBuffer).toBeInstanceOf(Float32Array);
});
```

## File Organization for Performance

### Structure Pattern
```
src/
├── core/
│   └── performance/
│       ├── PerformanceMonitor.ts     # Singleton monitor
│       ├── usePerformanceMetrics.ts  # React hook
│       └── index.ts                  # Barrel exports
├── features/
│   └── [feature]/
│       ├── hooks/
│       │   ├── useWebSocket.ts       # Event-driven WebSocket
│       │   └── useOscilloscope.ts    # CircularBuffer usage
│       └── utils/
│           └── CircularBuffer.ts     # Efficient data structure
```

## Code Review Checklist

### Performance Review Points
- [ ] No `setInterval` used for state synchronization
- [ ] `Float32Array` used for numerical data instead of `number[]`
- [ ] CircularBuffer used for high-frequency data updates
- [ ] Canvas rendering is data-driven, not continuous
- [ ] Performance monitoring integrated
- [ ] Memory cleanup implemented in useEffect returns
- [ ] Expensive calculations are memoized
- [ ] Event-driven patterns used instead of polling

### Anti-Patterns to Avoid
- ❌ `setInterval` for state sync
- ❌ Array spreading for large datasets (`[...array, ...newItems]`)
- ❌ Continuous animation loops
- ❌ Creating objects in render functions
- ❌ Missing cleanup in useEffect
- ❌ Using `number[]` for high-frequency numerical data

## Related Documentation
- `CircularBuffer.ts` - High-performance data structure implementation
- `PerformanceMonitor.ts` - Application-wide performance tracking
- `useWebSocket.ts` - Event-driven WebSocket patterns
- `useCanvas.ts` - Data-driven canvas rendering
