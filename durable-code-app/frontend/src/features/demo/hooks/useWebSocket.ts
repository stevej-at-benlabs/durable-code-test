/**
 * Purpose: Custom React hook for WebSocket connection management in oscilloscope demo
 * Scope: Hook for managing WebSocket connections, state, and event handling
 * Overview: Provides a React hook interface to the WebSocket service with automatic
 *     connection management, state tracking, and cleanup. Handles connection lifecycle
 *     and provides reactive state updates for React components.
 * Dependencies: React hooks, WebSocket service, oscilloscope types
 * Exports: useWebSocket hook
 * Interfaces: Hook return type with connection state and methods
 * Implementation: React hook wrapping WebSocket service with proper lifecycle management
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { OscilloscopeData, WebSocketCommand } from '../types/oscilloscope.types';
import { getWebSocketSingleton } from '../services/websocketSingleton';

interface UseWebSocketReturn {
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  lastData: OscilloscopeData | null;
  send: (command: WebSocketCommand) => boolean;
  connect: () => Promise<void>;
  disconnect: () => void;
  reconnectAttempts: number;
}

export function useWebSocket(url?: string): UseWebSocketReturn {
  // Get singleton service first
  const service = getWebSocketSingleton();

  // Initialize state based on service's current state
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastData, setLastData] = useState<OscilloscopeData | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const hasInitializedRef = useRef(false);
  const mountedRef = useRef(true);

  // Setup event listeners
  useEffect(() => {
    if (!service) return;

    const handleOpen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      setError(null);
      setReconnectAttempts(0);
    };

    const handleClose = () => {
      setIsConnected(false);
      setIsConnecting(false);
    };

    const handleError = (error: Error) => {
      setError(error);
      setIsConnecting(false);
    };

    const handleData = (data: OscilloscopeData) => {
      setLastData(data);
      setError(null); // Clear error on successful data
    };

    const handleReconnecting = (data: { attempt: number }) => {
      setReconnectAttempts(data.attempt);
      setIsConnecting(true);
    };

    const handleReconnected = () => {
      setReconnectAttempts(0);
    };

    const handleMaxReconnectAttempts = () => {
      setError(new Error('Maximum reconnection attempts reached'));
      setIsConnecting(false);
    };

    // Add event listeners
    service.on('open', handleOpen);
    service.on('close', handleClose);
    service.on('error', handleError);
    service.on('data', handleData);
    service.on('reconnecting', handleReconnecting);
    service.on('reconnected', handleReconnected);
    service.on('maxReconnectAttemptsReached', handleMaxReconnectAttempts);

    // Cleanup listeners
    return () => {
      service.off('open', handleOpen);
      service.off('close', handleClose);
      service.off('error', handleError);
      service.off('data', handleData);
      service.off('reconnecting', handleReconnecting);
      service.off('reconnected', handleReconnected);
      service.off('maxReconnectAttemptsReached', handleMaxReconnectAttempts);
    };
  }, [service]);

  // Connect function
  const connect = useCallback(async (): Promise<void> => {
    if (!service || isConnecting || isConnected) return;

    setIsConnecting(true);
    setError(null);

    try {
      await service.connect(url);
    } catch (error) {
      if (mountedRef.current) {
        setError(error as Error);
        setIsConnecting(false);
      }
      throw error;
    }
  }, [service, url, isConnecting, isConnected]);

  // Disconnect function
  const disconnect = useCallback(() => {
    if (!service) return;

    service.disconnect();
    setIsConnected(false);
    setIsConnecting(false);
    setReconnectAttempts(0);
  }, [service]);

  // Send function
  const send = useCallback(
    (command: WebSocketCommand): boolean => {
      if (!service) return false;
      return service.send(command);
    },
    [service],
  );

  // Auto-connect on mount and sync state
  useEffect(() => {
    if (!service || hasInitializedRef.current) return;

    hasInitializedRef.current = true;

    const initConnection = async () => {
      // First, check if already connected
      if (service.isConnected) {
        setIsConnected(true);
        setIsConnecting(false);
        return;
      }

      setIsConnecting(true);
      setError(null);

      try {
        await service.connect(url);
        // Check state after connection attempt
        if (service.isConnected) {
          setIsConnected(true);
          setIsConnecting(false);
        }
      } catch (error) {
        setError(error as Error);
        setIsConnecting(false);
      }
    };

    // Run immediately
    initConnection();
  }, [service, url]);

  // Sync initial state with service (no polling needed - events handle updates)
  useEffect(() => {
    if (!service) return;

    // One-time state sync on service change
    setIsConnected(service.isConnected);
    if (!service.isConnected) {
      setIsConnecting(false);
    }
  }, [service]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      hasInitializedRef.current = false;
      // Don't disconnect the singleton - it should persist
    };
  }, []);

  return {
    isConnected,
    isConnecting,
    error,
    lastData,
    send,
    connect,
    disconnect,
    reconnectAttempts,
  };
}
