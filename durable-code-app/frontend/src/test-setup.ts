/**
 * Purpose: Global test setup and configuration for Vitest and React Testing Library
 * Scope: Test environment initialization, custom matchers, and global utilities
 * Created: 2025-09-12
 * Updated: 2025-09-12
 * Author: Development Team
 * Version: 1.0
 */

import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock window.location methods that are used in the app
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000/',
    assign: vi.fn(),
    reload: vi.fn(),
    replace: vi.fn(),
  },
  writable: true,
});

// Global test utilities
export const mockFetch = (response: unknown) => {
  globalThis.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(response),
      text: () => Promise.resolve(response),
    } as Response),
  ) as ReturnType<typeof vi.fn>;
};

export const mockFailedFetch = (status = 404) => {
  globalThis.fetch = vi.fn(() =>
    Promise.resolve({
      ok: false,
      status,
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
    } as Response),
  ) as ReturnType<typeof vi.fn>;
};
