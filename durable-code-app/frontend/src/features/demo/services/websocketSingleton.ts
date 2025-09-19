/**
 * Purpose: Singleton WebSocket service instance for oscilloscope demo
 * Scope: Global WebSocket connection management outside React lifecycle
 * Overview: Creates a single WebSocket service instance that persists across
 *     React component re-renders and StrictMode double-invocations. This pattern
 *     avoids the connection/disconnection cycles caused by React's StrictMode.
 * Dependencies: WebSocketService
 * Exports: webSocketSingleton instance
 * Implementation: Module-scoped singleton pattern
 */

import { WebSocketService } from './websocketService';

// Create a single instance that persists across React re-renders
let instance: WebSocketService | null = null;

/**
 * Get or create the singleton WebSocket service instance
 */
export function getWebSocketSingleton(): WebSocketService {
  if (!instance) {
    instance = new WebSocketService();
  }
  return instance;
}

/**
 * Reset the singleton (mainly for testing)
 */
export function resetWebSocketSingleton(): void {
  if (instance) {
    instance.disconnect();
    instance = null;
  }
}
