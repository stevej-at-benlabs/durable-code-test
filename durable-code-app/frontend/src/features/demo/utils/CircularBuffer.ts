/**
 * Purpose: High-performance circular buffer for oscilloscope data handling
 * Scope: Data structure for efficient streaming data storage with fixed memory footprint
 * Overview: Provides a circular buffer implementation optimized for real-time data streams.
 *     Eliminates array creation on every update by using a fixed-size buffer with
 *     circular indexing. Supports batch operations and efficient data views.
 * Dependencies: None (pure TypeScript)
 * Exports: CircularBuffer class
 * Interfaces: CircularBuffer with push, getView, and management methods
 * Implementation: Ring buffer using Float32Array for optimal memory layout and performance
 */

export class CircularBuffer {
  private buffer: Float32Array;
  private writeIndex: number = 0;
  private count: number = 0;
  private readonly maxSize: number;

  constructor(maxSize: number) {
    this.maxSize = maxSize;
    this.buffer = new Float32Array(maxSize);
  }

  /**
   * Add multiple items to the buffer efficiently
   * @param items Array of numbers to add
   */
  push(items: number[]): void {
    if (items.length === 0) return;

    for (let i = 0; i < items.length; i++) {
      this.buffer[this.writeIndex] = items[i];
      this.writeIndex = (this.writeIndex + 1) % this.maxSize;

      if (this.count < this.maxSize) {
        this.count++;
      }
    }
  }

  /**
   * Get a view of the current data in correct chronological order
   * Returns a new Float32Array that can be used for rendering
   */
  getView(): Float32Array {
    if (this.count === 0) {
      return new Float32Array(0);
    }

    const result = new Float32Array(this.count);

    if (this.count < this.maxSize) {
      // Buffer not full yet - data is at start of buffer
      result.set(this.buffer.subarray(0, this.count));
    } else {
      // Buffer is full - need to reconstruct order
      const oldestIndex = this.writeIndex;
      const firstPart = this.buffer.subarray(oldestIndex);
      const secondPart = this.buffer.subarray(0, oldestIndex);

      result.set(firstPart, 0);
      result.set(secondPart, firstPart.length);
    }

    return result;
  }

  /**
   * Get the most recent N samples efficiently
   * @param count Number of recent samples to get
   */
  getRecentSamples(count: number): Float32Array {
    const actualCount = Math.min(count, this.count);
    if (actualCount === 0) return new Float32Array(0);

    const result = new Float32Array(actualCount);

    if (this.count < this.maxSize) {
      // Buffer not full - get from end
      const start = Math.max(0, this.count - actualCount);
      result.set(this.buffer.subarray(start, this.count));
    } else {
      // Buffer is full - calculate positions
      let sourceIndex = (this.writeIndex - actualCount + this.maxSize) % this.maxSize;

      for (let i = 0; i < actualCount; i++) {
        result[i] = this.buffer[sourceIndex];
        sourceIndex = (sourceIndex + 1) % this.maxSize;
      }
    }

    return result;
  }

  /**
   * Get current buffer statistics
   */
  getStats(): { size: number; maxSize: number; utilizationPercent: number } {
    return {
      size: this.count,
      maxSize: this.maxSize,
      utilizationPercent: (this.count / this.maxSize) * 100,
    };
  }

  /**
   * Clear the buffer
   */
  clear(): void {
    this.writeIndex = 0;
    this.count = 0;
    // No need to clear the Float32Array - we track valid data with count
  }

  /**
   * Check if buffer is empty
   */
  isEmpty(): boolean {
    return this.count === 0;
  }

  /**
   * Check if buffer is at capacity
   */
  isFull(): boolean {
    return this.count === this.maxSize;
  }

  /**
   * Get current size
   */
  get size(): number {
    return this.count;
  }
}
