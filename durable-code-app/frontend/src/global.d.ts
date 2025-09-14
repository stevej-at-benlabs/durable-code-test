/**
 * Purpose: Global type definitions for test environment
 * Scope: TypeScript type definitions for global objects
 * Created: 2025-09-14
 * Updated: 2025-09-14
 * Author: Development Team
 * Version: 1.0
 */

declare global {
  var global: typeof globalThis;
  var fetch: typeof globalThis.fetch;
}

export {};
